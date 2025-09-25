"""
Benchmark script for the PV Finder agent.
Tests all examples in the query database and reports success rate.
Runs the PV finder agent against a benchmark dataset to evaluate performance.
Generates visualizations and detailed analysis.
"""

import os
import sys
import json
import time
from typing import List, Dict, Any, Tuple
import random
import argparse
import asyncio
import uuid
import requests

from datetime import datetime
import subprocess
from dotenv import load_dotenv








# Load environment variables from .env file
load_dotenv()

# Add the project root directory to sys.path using environment variable
project_root = os.environ.get("PROJECT_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)

# Add src directory to path as well since imports are from src/
src_path = os.path.join(project_root, "src")
if os.path.exists(src_path):
    sys.path.insert(0, src_path)


os.environ["AO_DB_HOST"] = "localhost"

from applications.als_assistant.services.pv_finder.util import initialize_nltk_resources
initialize_nltk_resources()

# Import the PV finder agent
from applications.als_assistant.services.pv_finder.agent import run_pv_finder_graph
from applications.als_assistant.services.pv_finder.core import PVSearchResult

# Observability and tracing disabled for benchmarking
tracer = None

# Import utilities from benchmark_utils.py
from applications.als_assistant.benchmarks.pv_finder.benchmark_utils import (
    load_query_database,
    evaluate_result,
    generate_analysis
)

# Use global logger
from configs.logger import get_logger
logger = get_logger("als_assistant", "pv_finder")

# Predefined model configurations for benchmarking
BENCHMARK_MODELS = [
    {"provider": "cborg", "model_id": "lbl/cborg-chat:latest"},
    # {"provider": "cborg", "model_id": "google/gemini-flash-lite"},
    # {"provider": "cborg", "model_id": "openai/gpt-4o-mini"},
    # {"provider": "cborg", "model_id": "anthropic/claude-sonnet"},
    # {"provider": "cborg", "model_id": "google/gemini-flash"},
]

def get_model_configuration() -> Dict[str, str]:
    """
    Retrieve model configuration using the utility function.
    
    Returns:
        Dictionary with model provider and ID information
    """
    try:
        # Import the model config utility
        from configs.config import get_model_config
        
        # Get PV finder model configurations using the utility function
        keyword_config = get_model_config("als_assistant", "pv_finder", "keyword")
        query_splitter_config = get_model_config("als_assistant", "pv_finder", "query_splitter")
        pv_query_config = get_model_config("als_assistant", "pv_finder", "pv_query")
        
        model_config = {
            "keyword_model_provider": keyword_config.get("provider", "unknown"),
            "keyword_model_id": keyword_config.get("model_id", "unknown"),
            "query_splitter_model_provider": query_splitter_config.get("provider", "unknown"),
            "query_splitter_model_id": query_splitter_config.get("model_id", "unknown"),
            "pv_query_model_provider": pv_query_config.get("provider", "unknown"),
            "pv_query_model_id": pv_query_config.get("model_id", "unknown"),
        }
        
        return model_config
        
    except Exception as e:
        logger.warning(f"Unexpected error getting model configuration: {e}")
        return {
            "error": f"Unexpected error: {str(e)}"
        }

def _get_cborg_api_usage() -> float:
    """
    Get current CBORG API usage/cost from the API.
    
    Returns:
        Current usage cost as a float, or 0.0 if unable to retrieve
    """
    try:
        api_key = os.getenv("CBORG_API_KEY")
        if not api_key:
            logger.warning("CBORG_API_KEY not found in environment variables")
            return 0.0
        
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        response = requests.get(
            "https://api.cborg.lbl.gov/key/info",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            usage = data.get("info", {}).get("spend", 0.0)
            logger.debug(f"Current CBORG API usage: ${usage:.4f}")
            return float(usage)
        else:
            logger.warning(f"Failed to get CBORG usage info: HTTP {response.status_code}")
            return 0.0
            
    except Exception as e:
        logger.warning(f"Error retrieving CBORG API usage: {e}")
        return 0.0

def setup_model_override(provider: str, model_id: str):
    """
    Set up model configuration override using monkey patching.
    
    This approach temporarily overrides the get_model_config function to return
    our desired model configuration without modifying any files.
    
    Args:
        provider: Model provider (e.g., 'cborg', 'openai', 'anthropic')
        model_id: Model identifier (e.g., 'google/gemini-flash')
    """
    try:
        # Import the config module to monkey patch
        from configs import config
        
        # Store the original function
        if not hasattr(setup_model_override, '_original_get_model_config'):
            setup_model_override._original_get_model_config = config.get_model_config
        
        # Create the override function
        def override_get_model_config(app_or_framework: str, service: str = None, model_type: str = None):
            # Only override PV finder model configs
            if app_or_framework == "als_assistant" and service == "pv_finder":
                return {
                    "provider": provider,
                    "model_id": model_id,
                    "max_tokens": 4096
                }
            # For all other configs, use the original function
            return setup_model_override._original_get_model_config(app_or_framework, service, model_type)
        
        # Apply the monkey patch
        config.get_model_config = override_get_model_config
        
        logger.info(f"Set up model override for: {provider}/{model_id}")
        
    except Exception as e:
        logger.error(f"Failed to set up model override: {e}")
        raise

def restore_original_model_config():
    """
    Restore the original model configuration function.
    """
    try:
        from configs import config
        
        if hasattr(setup_model_override, '_original_get_model_config'):
            config.get_model_config = setup_model_override._original_get_model_config
            logger.info("Restored original model configuration")
        
    except Exception as e:
        logger.warning(f"Failed to restore original model config: {e}")

async def run_agent(query: str, target_pvs: List[str], session_id: str = None, user_id: str = None) -> List:
    """
    Run the PV finder agent directly.
    
    Args:
        query: The user query string
        target_pvs: List of target PVs for evaluation
        session_id: Session ID for the benchmark run (optional, unused)
        user_id: User ID for the benchmark run (optional, unused)
        
    Returns:
        List in format [pv_list, explanation] where pv_list is a list of PV strings
    """
    try:
        # Call the PV finder agent directly
        result = await run_pv_finder_graph(query)
        
        # Extract PVs and description from PVSearchResult object
        pvs = result.pvs if result.pvs else []
        explanation = result.description if result.description else "No description provided."
        
        # Return in the expected format [pv_list, explanation]
        return [pvs, explanation]
                
    except Exception as e:
        logger.error(f"Error calling PV finder agent: {e}")
        raise

async def run_single_model_benchmark(
    provider: str, 
    model_id: str, 
    queries: List[Dict], 
    benchmark_session_id: str, 
    benchmark_user_id: str
) -> Dict[str, Any]:
    """
    Run benchmark for a single model configuration.
    
    Args:
        provider: Model provider
        model_id: Model identifier  
        queries: List of benchmark queries
        benchmark_session_id: Session ID for the benchmark
        benchmark_user_id: User ID for the benchmark
        
    Returns:
        Dictionary with benchmark results and summary
    """
    print(f"\n{'='*60}")
    print(f"RUNNING BENCHMARK FOR: {provider}/{model_id}")
    print(f"{'='*60}")
    
    # Create individual timestamped output directory for this run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_base_dir = os.path.join(os.path.dirname(__file__), "benchmark_runs")
    output_dir = os.path.join(output_base_dir, f"run_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Benchmark output directory: {output_dir}")
    
    # Set model configuration via monkey patching (safer than file modification)
    print(f"Setting model configuration to {provider}/{model_id} via runtime override...")
    setup_model_override(provider, model_id)
    
    # Get model configuration for reporting
    model_config = get_model_configuration()
    print(f"Model configuration: {json.dumps(model_config, indent=2)}")
    
    # Get initial CBORG API usage for cost tracking
    print("Checking initial CBORG API usage for cost tracking...")
    initial_usage = _get_cborg_api_usage()
    print(f"Initial CBORG API usage: ${initial_usage:.4f}")
    
    # Prepare results tracking
    results = []
    success_count = 0
    partial_count = 0
    failure_count = 0
    total_count = len(queries)
    
    # Run the benchmark
    start_time = time.time()
    for idx, query in enumerate(queries):
        user_query = query["user_query"]
        target_pvs = query["targeted_pv"]
        
        print(f"\n[{idx+1}/{total_count}] Processing query: '{user_query}'")
        query_start_time = time.time()
        
        # Run the agent
        try:              
            result = await run_agent(user_query, target_pvs, session_id=benchmark_session_id, user_id=benchmark_user_id)
            
            # The run_agent function now returns [pv_list, explanation] format directly
            status, score = evaluate_result(result, target_pvs)
            
            # Update counters
            if status == "success":
                success_count += 1
            elif status == "partial":
                partial_count += 1
            else:
                failure_count += 1
                
            result_item = {
                "query": user_query,
                "target_pvs": target_pvs,
                "result": result,
                "status": status,
                "score": score
            }
            results.append(result_item)
            
            # Print intermediate result
            query_time = time.time() - query_start_time
            print(f"  Status: {status.upper()}, Score: {score:.2%}, Time: {query_time:.2f}s")
            print(f"  Target PVs: {', '.join(target_pvs)}")
            if isinstance(result, list) and len(result) >= 1:
                found_pvs = result[0] if isinstance(result[0], list) else []
                print(f"  Found PVs: {', '.join(found_pvs) if found_pvs else 'None'}")
            
            # Save intermediate results to file (every 10 queries)
            if (idx + 1) % 10 == 0:
                intermediate_results_path = os.path.join(output_dir, "benchmark_results_intermediate.json")
                current_success_rate = success_count / (idx + 1) if (idx + 1) > 0 else 0
                current_partial_rate = partial_count / (idx + 1) if (idx + 1) > 0 else 0
                current_failure_rate = failure_count / (idx + 1) if (idx + 1) > 0 else 0
                current_avg_score = sum(r["score"] for r in results) / (idx + 1) if (idx + 1) > 0 else 0
                
                # Get current usage for cost tracking
                current_usage = _get_cborg_api_usage()
                current_cost = current_usage - initial_usage
                
                with open(intermediate_results_path, 'w') as f:
                    json.dump({
                        "summary": {
                            "agent_type": "direct_pv_finder",
                            "model_config": model_config,
                            "session_id": benchmark_session_id,
                            "user_id": benchmark_user_id,
                            "total_queries": idx + 1,
                            "queries_remaining": total_count - (idx + 1),
                            "total_time": f"{time.time() - start_time:.0f}",
                            "avg_time_per_query": f"{(time.time() - start_time) / (idx + 1) if (idx + 1) > 0 else 0:.2f}",
                            "success_rate": f"{current_success_rate:.2%}",
                            "partial_rate": f"{current_partial_rate:.2%}",
                            "failure_rate": f"{current_failure_rate:.2%}",
                            "average_score": f"{current_avg_score:.2%}",
                            "current_cost": f"${current_cost:.4f}",
                            "cost_per_query": f"${current_cost / (idx + 1) if (idx + 1) > 0 else 0:.4f}"
                        },
                        "results": results
                    }, f, indent=2)
                
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            results.append({
                "query": user_query,
                "target_pvs": target_pvs,
                "result": f"ERROR: {str(e)}",
                "status": "error",
                "score": 0.0
            })
            failure_count += 1
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Get final CBORG API usage for cost tracking
    print("Checking final CBORG API usage for cost tracking...")
    final_usage = _get_cborg_api_usage()
    benchmark_cost = final_usage - initial_usage
    print(f"Final CBORG API usage: ${final_usage:.4f}")
    print(f"Benchmark cost: ${benchmark_cost:.4f}")
    
    # Calculate final metrics
    success_rate = success_count / total_count
    partial_rate = partial_count / total_count
    failure_rate = failure_count / total_count if total_count > 0 else 0
    average_score = sum(r["score"] for r in results) / total_count if total_count > 0 else 0
    
    # Print summary
    print("\n" + "="*50)
    print(f"BENCHMARK SUMMARY ({provider}/{model_id})")
    print("="*50)
    print(f"Total queries: {total_count}")
    print(f"Time taken: {total_time:.2f} seconds")
    avg_time_query = total_time/total_count if total_count > 0 else 0
    print(f"Average time per query: {avg_time_query:.2f} seconds")
    print(f"Success rate: {success_rate:.2%} ({success_count}/{total_count})")
    print(f"Partial success rate: {partial_rate:.2%} ({partial_count}/{total_count})")
    print(f"Failure rate: {failure_rate:.2%} ({failure_count}/{total_count})")
    print(f"Average score: {average_score:.2%}")
    print(f"Total cost: ${benchmark_cost:.4f}")
    if total_count > 0:
        cost_per_query = benchmark_cost / total_count
        print(f"Cost per query: ${cost_per_query:.4f}")
    print("="*50)
    
    # Create summary for analysis and visualization
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary = {
        "agent_type": "direct_pv_finder",
        "model_config": model_config,
        "session_id": benchmark_session_id,
        "user_id": benchmark_user_id,
        "timestamp": timestamp,
        "total_queries": total_count,
        "total_time": total_time,
        "avg_time_per_query": total_time/total_count if total_count > 0 else 0,
        "success_rate": success_rate,
        "partial_rate": partial_rate,
        "failure_rate": failure_rate,
        "average_score": average_score,
        "initial_usage": initial_usage,
        "final_usage": final_usage,
        "benchmark_cost": benchmark_cost,
        "cost_per_query": benchmark_cost / total_count if total_count > 0 else 0.0
    }
    
    # Save final results to file
    results_path = os.path.join(output_dir, "benchmark_results_final.json")
    with open(results_path, 'w') as f:
        json.dump({
            "summary": summary,
            "results": results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to {results_path}")
    
    # Generate analysis and visualizations for this individual run
    print("Generating analysis and visualizations...")
    generate_analysis(summary, results, output_dir)
    
    print(f"All output files are in: {output_dir}")
    
    # Restore original model configuration
    restore_original_model_config()
    
    return {
        "summary": summary,
        "results": results,
        "results_path": results_path,
        "output_dir": output_dir
    }

async def main(): # Changed to async
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run PV Finder agent benchmark')
    parser.add_argument('--limit', type=int, default=None, help='Limit the number of queries to run')
    parser.add_argument('--start-index', type=int, default=0, help='Start from this query index')
    parser.add_argument('--random-sample', action='store_true', help='Use random sampling of queries instead of sequential')
    parser.add_argument('--multi-model', action='store_true', help='Run benchmark on all predefined models')
    parser.add_argument('--model', type=str, default=None, help='Run benchmark on specific model (format: provider/model_id or just model_id for cborg)')
    parser.add_argument('--repeat', type=int, default=1, help='Number of times to repeat each model benchmark (default: 1)')
    args = parser.parse_args()
    
    # Generate unique session ID and user ID for this benchmark session
    session_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    benchmark_session_id = f"benchmark_run_{session_timestamp}_{uuid.uuid4().hex[:8]}"
    benchmark_user_id = f"benchmark_user_{session_timestamp}"
    
    print(f"Benchmark session ID: {benchmark_session_id}")
    print(f"Benchmark user ID: {benchmark_user_id}")
    
    # Load the query database
    database_path = os.path.join(os.path.dirname(__file__), "benchmark_database.json")
    print(f"Loading queries from {database_path}")
    all_queries = load_query_database(database_path)
    
    # Apply filtering based on command line arguments
    if args.random_sample and args.limit:
        # Random sampling with specified limit
        if args.limit > len(all_queries):
            print(f"Warning: Requested limit {args.limit} exceeds available queries {len(all_queries)}")
            args.limit = len(all_queries)
        
        queries = random.sample(all_queries, args.limit)
        print(f"Running benchmark with {len(queries)} randomly sampled queries")
    else:
        # Sequential selection with optional limit and start index
        start_idx = min(args.start_index, len(all_queries) - 1)
        if args.limit:
            end_idx = min(start_idx + args.limit, len(all_queries))
            queries = all_queries[start_idx:end_idx]
            print(f"Running benchmark with {len(queries)} queries (indices {start_idx}-{end_idx-1})")
        else:
            queries = all_queries[start_idx:]
            print(f"Running benchmark with {len(queries)} queries (starting from index {start_idx})")
    
    # Determine which models to benchmark
    models_to_test = []
    
    if args.multi_model:
        # Use all predefined models
        models_to_test = BENCHMARK_MODELS.copy()
        print(f"Multi-model mode: Testing {len(models_to_test)} models")
    elif args.model:
        # Parse single model specification
        if '/' in args.model:
            provider, model_id = args.model.split('/', 1)
        else:
            provider, model_id = "cborg", args.model  # Default to cborg provider
        
        models_to_test = [{"provider": provider, "model_id": model_id}]
        print(f"Single model mode: Testing {provider}/{model_id}")
    else:
        # Use current configuration (default behavior)
        current_config = get_model_configuration()
        if "pv_query_model_provider" in current_config and "pv_query_model_id" in current_config:
            models_to_test = [{
                "provider": current_config["pv_query_model_provider"],
                "model_id": current_config["pv_query_model_id"]
            }]
        else:
            # Fallback to first model in list
            models_to_test = [BENCHMARK_MODELS[0]]
        print(f"Using current/default model configuration")
    
    # Track all benchmark results
    all_benchmark_results = []
    
    # Run benchmarks: repeat loop outer, multi-model loop inner
    total_runs = len(models_to_test) * args.repeat
    current_run = 0
    
    for repeat_num in range(args.repeat):
        print(f"\n{'*'*100}")
        print(f"REPEAT CYCLE {repeat_num + 1}/{args.repeat}")
        print(f"{'*'*100}")
        
        for model_config in models_to_test:
            provider = model_config["provider"]
            model_id = model_config["model_id"]
            
            current_run += 1
            print(f"\n{'#'*80}")
            print(f"RUN {current_run}/{total_runs}: {provider}/{model_id} (Cycle {repeat_num + 1}/{args.repeat})")
            print(f"{'#'*80}")
            
            try:
                # Run benchmark for this model
                benchmark_result = await run_single_model_benchmark(
                    provider=provider,
                    model_id=model_id,
                    queries=queries,
                    benchmark_session_id=benchmark_session_id,
                    benchmark_user_id=benchmark_user_id
                )
                
                all_benchmark_results.append(benchmark_result)
                
            except Exception as e:
                print(f"ERROR: Failed to run benchmark for {provider}/{model_id}: {e}")
                logger.error(f"Benchmark failed for {provider}/{model_id}: {e}", exc_info=True)
    
    # Print overall summary
    print(f"\n{'='*80}")
    print(f"OVERALL BENCHMARK SUMMARY")
    print(f"{'='*80}")
    print(f"Total benchmark runs completed: {len(all_benchmark_results)}/{total_runs}")
    print(f"Models tested: {len(models_to_test)}")
    print(f"Repeats per model: {args.repeat}")
    print(f"Queries per run: {len(queries)}")
    
    # Show individual output directories
    print(f"\nIndividual run directories:")
    for i, result in enumerate(all_benchmark_results):
        run_dir = result["output_dir"]
        model_info = result["summary"]["model_config"]
        model_id = model_info.get("pv_query_model_id", "unknown")
        success_rate = result["summary"]["success_rate"]
        cost = result["summary"]["benchmark_cost"]
        print(f"  Run {i+1}: {model_id} -> {run_dir}")
        print(f"    Success: {success_rate:.2%}, Cost: ${cost:.4f}")
    
    # Calculate total cost across all runs
    total_cost = sum(result["summary"]["benchmark_cost"] for result in all_benchmark_results)
    print(f"\nTotal cost across all runs: ${total_cost:.4f}")
    
    print(f"{'='*80}")
    
    # Note about analysis
    if all_benchmark_results:
        print("\nEach run includes:")
        print("  - benchmark_results_final.json (detailed results)")
        print("  - benchmark_results_intermediate.json (progress tracking)")
        print("  - analysis.txt (text summary)")
        print("  - score_distribution.png (score visualization)")
        print("  - success_rate_pie.png (success rate breakdown)")
        print("\nRun 'python analyze_benchmark_results.py' to generate cross-model comparison plots.")

if __name__ == "__main__":
    asyncio.run(main()) # Changed to asyncio.run
 