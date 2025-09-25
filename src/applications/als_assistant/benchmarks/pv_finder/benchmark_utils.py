"""
Utility functions for the PV finder benchmark script.
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any, Tuple
from datetime import datetime

def load_query_database(filepath: str) -> List[Dict[str, Any]]:
    """Load test queries from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def evaluate_result(result: List, target_pvs: List[str]) -> Tuple[str, float]:
    """
    Evaluate if the agent found the target PVs.
    
    The agent returns results in the format [pv_list, explanation] where pv_list
    is a list of strings representing PVs.
    
    Returns:
        Tuple of (status, score) where:
        - status is one of "success", "partial", "failure"
        - score is the fraction of target PVs found (0.0 to 1.0)
    """
    # Extract PVs from result if it has the expected format [pv_list, explanation]
    if isinstance(result, list) and len(result) >= 1:
        result_pvs = result[0] if isinstance(result[0], list) else []
    else:
        # Fallback for unexpected formats
        result_pvs = []
        # Consider adding logging here if used in a context with a logger
        # import logging
        # logging.warning(f"Unexpected result format for evaluation: {result}")
        
    # Check if all target PVs are in the result
    found_target_pvs = []
    for pv in target_pvs:
        if pv in result_pvs:
            found_target_pvs.append(pv)
    
    # Check if all result PVs are in the target (new bidirectional check)
    found_result_pvs = []
    for pv in result_pvs:
        if pv in target_pvs:
            found_result_pvs.append(pv)
    
    # Calculate scores in both directions
    target_score = len(found_target_pvs) / len(target_pvs) if target_pvs else 0.0
    # result_score = len(found_result_pvs) / len(result_pvs) if result_pvs else 0.0 # Not directly used in final score logic
    
    # Check for exact match (all target PVs found, no extra PVs)
    exact_match = (len(found_target_pvs) == len(target_pvs) and len(found_result_pvs) == len(result_pvs))
    
    # Calculate combined score - giving more weight to finding targets, but penalizing extra PVs
    if exact_match:
        score = 1.0
        return "success", score
    elif len(found_target_pvs) > 0:
        # Target PVs found but with extras, or not all targets found
        # Use target_score but cap at 0.5 if there are extra PVs
        if len(result_pvs) > len(target_pvs):
            score = min(0.5, target_score)
        else:
            score = target_score
        return "partial", score
    else:
        return "failure", 0.0

def plot_success_rate_pie(summary: Dict[str, Any], save_path: str = None):
    """Create a pie chart showing success/partial/failure rates."""
    labels = ['Success', 'Partial', 'Failure']
    sizes = [
        summary['success_rate'],
        summary['partial_rate'],
        summary['failure_rate']
    ]
    colors = ['#4CAF50', '#FFC107', '#F44336']
    explode = (0.1, 0, 0)  # explode the 1st slice (Success)
    
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures the pie is circular
    plt.title('PV Finder Success Rate')
    
    if save_path:
        plt.savefig(save_path)
    plt.close()

def plot_score_distribution(results: List[Dict[str, Any]], save_path: str = None):
    """Create a histogram of score distribution."""
    scores = [r['score'] for r in results]
    
    plt.figure(figsize=(10, 6))
    plt.hist(scores, bins=10, alpha=0.7, color='blue', edgecolor='black')
    plt.title('Distribution of Scores')
    plt.xlabel('Score (fraction of correct PVs)')
    plt.ylabel('Number of Queries')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    if save_path:
        plt.savefig(save_path)
    plt.close()

def identify_difficult_queries(results: List[Dict[str, Any]], threshold: float = 0.5) -> List[Dict[str, Any]]:
    """Identify queries that performed poorly."""
    return [r for r in results if r['score'] < threshold]

def generate_analysis(summary: Dict[str, Any], results: List[Dict[str, Any]], output_dir: str):
    """Generate analysis and visualizations from benchmark results."""
    # Generate visualizations
    plot_success_rate_pie(summary, save_path=os.path.join(output_dir, "success_rate_pie.png"))
    plot_score_distribution(results, save_path=os.path.join(output_dir, "score_distribution.png"))
    
    # Identify difficult queries
    difficult_queries = identify_difficult_queries(results)
    
    # Count cases with extra PVs returned
    extra_pv_cases = []
    for r in results:
        if isinstance(r['result'], list) and len(r['result']) >= 1:
            result_pvs = r['result'][0] if isinstance(r['result'][0], list) else []
            target_pvs = r['target_pvs']
            if len(result_pvs) > len(target_pvs) and any(pv in result_pvs for pv in target_pvs):
                extra_pv_cases.append(r)
    
    # Save analysis to file
    analysis_path = os.path.join(output_dir, "analysis.txt")
    with open(analysis_path, 'w') as f:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"PV FINDER BENCHMARK ANALYSIS (MCP PV FINDER) - Generated on {current_time}\n")
        f.write("=================================================\n\n")
        
        # Write summary
        f.write("SUMMARY STATISTICS\n")
        f.write("-----------------\n")
        f.write(f"Total queries tested: {summary['total_queries']}\n")
        f.write(f"Total time: {summary['total_time']:.2f} seconds\n")
        f.write(f"Average time per query: {summary['avg_time_per_query']:.2f} seconds\n")
        f.write(f"Success rate: {summary['success_rate']:.2%}\n")
        f.write(f"Partial success rate: {summary['partial_rate']:.2%}\n")
        f.write(f"Failure rate: {summary['failure_rate']:.2%}\n")
        f.write(f"Average score: {summary['average_score']:.2%}\n")
        f.write(f"Cases with extra PVs returned: {len(extra_pv_cases)} ({len(extra_pv_cases)/summary['total_queries'] if summary['total_queries'] > 0 else 0:.2%} of total)\n\n")
        
        # Write difficult queries
        f.write("DIFFICULT QUERIES\n")
        f.write("----------------\n")
        if difficult_queries:
            for i, q in enumerate(difficult_queries, 1):
                f.write(f"{i}. Query: \"{q['query']}\"\n")
                f.write(f"   Target PVs: {', '.join(q['target_pvs'])}\n")
                f.write(f"   Score: {q['score']:.2%}\n")
                f.write(f"   Status: {q['status']}\n\n")
        else:
            f.write("No particularly difficult queries found.\n\n")
        
        # Write perfect queries
        perfect_queries = [r for r in results if r['score'] == 1.0]
        f.write("PERFECT QUERIES\n")
        f.write("--------------\n")
        f.write(f"Number of queries with perfect score: {len(perfect_queries)} ({len(perfect_queries)/len(results) if results else 0:.2%} of total)\n\n")
        
        # Write cases with extra PVs
        f.write("QUERIES WITH EXTRA PVs\n")
        f.write("---------------------\n")
        if extra_pv_cases:
            for i, q in enumerate(extra_pv_cases, 1):
                f.write(f"{i}. Query: \"{q['query']}\"\n")
                f.write(f"   Target PVs: {', '.join(q['target_pvs'])}\n")
                if isinstance(q['result'], list) and len(q['result']) >= 1:
                    result_pvs = q['result'][0] if isinstance(q['result'][0], list) else []
                    f.write(f"   Found PVs: {', '.join(result_pvs)}\n")
                f.write(f"   Score: {q['score']:.2%}\n")
                f.write(f"   Status: {q['status']}\n\n")
        else:
            f.write("No queries returned extra PVs.\n\n")
    
    print(f"\nAnalysis complete. Results saved to {output_dir}")
    print(f"- Summary and analysis: {analysis_path}")
    print(f"- Visualizations: {output_dir}") 