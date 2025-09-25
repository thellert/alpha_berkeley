#!/usr/bin/env python3
"""
Script to analyze benchmark failures across all runs and models.
Identifies which benchmark queries failed most frequently and tracks failures by model.
"""

import json
import os
import pandas as pd
from collections import defaultdict, Counter
from pathlib import Path

def read_benchmark_failures(base_dir):
    """Read all benchmark result files and extract failure data."""
    all_results = []
    
    # Find all run directories
    run_dirs = [d for d in os.listdir(base_dir) if d.startswith('run_') and os.path.isdir(os.path.join(base_dir, d))]
    
    for run_dir in run_dirs:
        json_file = os.path.join(base_dir, run_dir, 'benchmark_results_final.json')
        
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                summary = data['summary']
                model_config = summary['model_config']
                model_id = model_config['pv_query_model_id']
                
                # Process each query result
                for result in data['results']:
                    query = result['query']
                    status = result['status']
                    score = result['score']
                    target_pvs = result['target_pvs']
                    found_pvs = result['result'][0] if result['result'] else []
                    
                    all_results.append({
                        'run_id': run_dir,
                        'model': model_id,
                        'query': query,
                        'status': status,
                        'score': score,
                        'target_pvs': target_pvs,
                        'found_pvs': found_pvs,
                        'num_target_pvs': len(target_pvs),
                        'num_found_pvs': len(found_pvs) if found_pvs else 0
                    })
                
                print(f"Processed {run_dir}: {model_id}")
                
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
    
    return all_results

def analyze_query_failures(results):
    """Analyze which queries failed most frequently across all models."""
    query_stats = defaultdict(lambda: {
        'total_attempts': 0,
        'failures': 0,
        'partial_successes': 0,
        'successes': 0,
        'models_failed': set(),
        'models_succeeded': set(),
        'failure_rate': 0.0
    })
    
    for result in results:
        query = result['query']
        status = result['status']
        model = result['model']
        
        query_stats[query]['total_attempts'] += 1
        
        if status == 'failure':
            query_stats[query]['failures'] += 1
            query_stats[query]['models_failed'].add(model)
        elif status == 'partial':
            query_stats[query]['partial_successes'] += 1
        else:  # success
            query_stats[query]['successes'] += 1
            query_stats[query]['models_succeeded'].add(model)
    
    # Calculate failure rates
    for query, stats in query_stats.items():
        stats['failure_rate'] = stats['failures'] / stats['total_attempts']
        stats['models_failed'] = list(stats['models_failed'])
        stats['models_succeeded'] = list(stats['models_succeeded'])
    
    return query_stats

def analyze_model_failures(results):
    """Analyze failures by model."""
    model_stats = defaultdict(lambda: {
        'total_queries': 0,
        'failures': 0,
        'partial_successes': 0,
        'successes': 0,
        'failed_queries': [],
        'failure_rate': 0.0
    })
    
    for result in results:
        model = result['model']
        status = result['status']
        query = result['query']
        
        model_stats[model]['total_queries'] += 1
        
        if status == 'failure':
            model_stats[model]['failures'] += 1
            model_stats[model]['failed_queries'].append(query)
        elif status == 'partial':
            model_stats[model]['partial_successes'] += 1
        else:  # success
            model_stats[model]['successes'] += 1
    
    # Calculate failure rates
    for model, stats in model_stats.items():
        stats['failure_rate'] = stats['failures'] / stats['total_queries']
    
    return model_stats

def create_failure_summary_table(query_stats):
    """Create a summary table of the most problematic queries."""
    # Sort queries by failure rate (descending)
    sorted_queries = sorted(query_stats.items(), key=lambda x: x[1]['failure_rate'], reverse=True)
    
    print("\n" + "="*120)
    print("MOST PROBLEMATIC BENCHMARK QUERIES")
    print("="*120)
    print(f"{'Query':<60} {'Failure Rate':<12} {'Failures':<10} {'Total':<8} {'Models Failed'}")
    print("-"*120)
    
    for query, stats in sorted_queries:
        if stats['failure_rate'] > 0:  # Only show queries that failed at least once
            models_failed_str = ", ".join([m.split('/')[-1] for m in stats['models_failed'][:3]])
            if len(stats['models_failed']) > 3:
                models_failed_str += f" (+{len(stats['models_failed'])-3} more)"
            
            query_short = query[:58] + ".." if len(query) > 60 else query
            
            print(f"{query_short:<60} {stats['failure_rate']:.3f} ({stats['failure_rate']*100:.1f}%)"
                  f"   {stats['failures']:<10} {stats['total_attempts']:<8} {models_failed_str}")
    
    print("="*120)

def create_model_failure_table(model_stats):
    """Create a table showing failures by model."""
    # Sort models by failure rate (ascending, so best models first)
    sorted_models = sorted(model_stats.items(), key=lambda x: x[1]['failure_rate'])
    
    print("\n" + "="*100)
    print("MODEL FAILURE ANALYSIS")
    print("="*100)
    print(f"{'Model':<30} {'Failure Rate':<15} {'Failures':<10} {'Partial':<10} {'Success':<10} {'Total'}")
    print("-"*100)
    
    for model, stats in sorted_models:
        model_short = model.split('/')[-1] if '/' in model else model
        print(f"{model_short:<30} {stats['failure_rate']:.3f} ({stats['failure_rate']*100:.1f}%)"
              f"     {stats['failures']:<10} {stats['partial_successes']:<10} "
              f"{stats['successes']:<10} {stats['total_queries']}")
    
    print("="*100)

def create_detailed_failure_matrix(results):
    """Create a detailed matrix showing which queries failed for which models."""
    # Create a pivot table-like structure
    failure_matrix = defaultdict(lambda: defaultdict(str))
    
    for result in results:
        query = result['query']
        model = result['model'].split('/')[-1]  # Just model name
        status = result['status']
        score = result['score']
        
        if status == 'failure':
            failure_matrix[query][model] = 'F'
        elif status == 'partial':
            failure_matrix[query][model] = f'P({score:.1f})'
        else:
            failure_matrix[query][model] = 'S'
    
    return failure_matrix

def save_detailed_failure_report(query_stats, model_stats, failure_matrix, results):
    """Save a detailed failure report to a text file."""
    
    with open('src/benchmarks/pv_finder/benchmark_failure_analysis.txt', 'w') as f:
        f.write("DETAILED BENCHMARK FAILURE ANALYSIS\n")
        f.write("="*80 + "\n\n")
        
        # Summary statistics
        total_queries = sum(stats['total_attempts'] for stats in query_stats.values())
        total_failures = sum(stats['failures'] for stats in query_stats.values())
        overall_failure_rate = total_failures / total_queries
        
        f.write(f"OVERALL STATISTICS:\n")
        f.write(f"Total query attempts: {total_queries}\n")
        f.write(f"Total failures: {total_failures}\n")
        f.write(f"Overall failure rate: {overall_failure_rate:.3f} ({overall_failure_rate*100:.1f}%)\n\n")
        
        # Most problematic queries
        f.write("MOST PROBLEMATIC QUERIES (sorted by failure rate):\n")
        f.write("-" * 80 + "\n")
        
        sorted_queries = sorted(query_stats.items(), key=lambda x: x[1]['failure_rate'], reverse=True)
        
        for query, stats in sorted_queries:
            if stats['failure_rate'] > 0:
                f.write(f"\nQuery: {query}\n")
                f.write(f"  Failure rate: {stats['failure_rate']:.3f} ({stats['failure_rate']*100:.1f}%)\n")
                f.write(f"  Failures: {stats['failures']}/{stats['total_attempts']}\n")
                f.write(f"  Models that failed: {', '.join(stats['models_failed'])}\n")
                f.write(f"  Models that succeeded: {', '.join(stats['models_succeeded'])}\n")
        
        # Model performance
        f.write(f"\n\nMODEL PERFORMANCE COMPARISON:\n")
        f.write("-" * 80 + "\n")
        
        sorted_models = sorted(model_stats.items(), key=lambda x: x[1]['failure_rate'])
        
        for model, stats in sorted_models:
            f.write(f"\nModel: {model}\n")
            f.write(f"  Failure rate: {stats['failure_rate']:.3f} ({stats['failure_rate']*100:.1f}%)\n")
            f.write(f"  Results: {stats['successes']} success, {stats['partial_successes']} partial, {stats['failures']} failures\n")
            if stats['failed_queries']:
                f.write(f"  Failed queries:\n")
                for query in stats['failed_queries']:
                    f.write(f"    - {query}\n")

def main():
    """Main function."""
    # Path to benchmark runs directory
    base_dir = 'src/benchmarks/pv_finder/benchmark_runs'
    
    print("Reading benchmark data...")
    results = read_benchmark_failures(base_dir)
    
    if not results:
        print("No benchmark data found!")
        return
    
    print(f"Loaded {len(results)} individual query results")
    
    # Analyze failures
    print("\nAnalyzing query failures...")
    query_stats = analyze_query_failures(results)
    
    print("Analyzing model failures...")
    model_stats = analyze_model_failures(results)
    
    print("Creating failure matrix...")
    failure_matrix = create_detailed_failure_matrix(results)
    
    # Display results
    create_failure_summary_table(query_stats)
    create_model_failure_table(model_stats)
    
    # Save detailed report
    print("\nSaving detailed failure analysis...")
    save_detailed_failure_report(query_stats, model_stats, failure_matrix, results)
    
    print("\nAnalysis complete!")
    print("- Summary tables displayed above")
    print("- Detailed report saved to 'benchmark_failure_analysis.txt'")
    
    # Print some quick insights
    total_unique_queries = len(query_stats)
    queries_with_failures = sum(1 for stats in query_stats.values() if stats['failure_rate'] > 0)
    
    print(f"\nQUICK INSIGHTS:")
    print(f"- {total_unique_queries} unique benchmark queries")
    print(f"- {queries_with_failures} queries failed at least once")
    print(f"- {total_unique_queries - queries_with_failures} queries succeeded on all models")

if __name__ == "__main__":
    main() 