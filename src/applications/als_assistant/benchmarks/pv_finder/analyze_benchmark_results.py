#!/usr/bin/env python3
"""
Script to analyze benchmark results and plot accuracy vs average time per query
for different models with error bars for multiple runs of the same model.
"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def read_benchmark_data(base_dir):
    """Read all benchmark result files and extract relevant data."""
    data = []
    
    # Find all run directories
    run_dirs = [d for d in os.listdir(base_dir) if d.startswith('run_') and os.path.isdir(os.path.join(base_dir, d))]
    
    for run_dir in run_dirs:
        json_file = os.path.join(base_dir, run_dir, 'benchmark_results_final.json')
        
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    results = json.load(f)
                
                summary = results['summary']
                model_config = summary['model_config']
                
                # Extract model information - using the pv_query_model as the primary model identifier
                model_id = model_config['pv_query_model_id']
                
                # Extract performance metrics
                success_rate = summary['success_rate']
                avg_time_per_query = summary['avg_time_per_query']
                
                # Extract cost metrics (with fallback for older runs without cost data)
                cost_per_query = summary.get('cost_per_query', 0.0)
                benchmark_cost = summary.get('benchmark_cost', 0.0)
                
                # Extract timestamp from run_id (format: run_YYYYMMDD_HHMMSS)
                try:
                    timestamp_str = run_dir.replace('run_', '')
                    timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                except ValueError:
                    # Fallback to file modification time if parsing fails
                    timestamp = datetime.fromtimestamp(os.path.getmtime(json_file))
                
                data.append({
                    'model': model_id,
                    'success_rate': success_rate,
                    'avg_time_per_query': avg_time_per_query,
                    'cost_per_query': cost_per_query,
                    'benchmark_cost': benchmark_cost,
                    'run_id': run_dir,
                    'timestamp': timestamp,
                    'has_cost_data': 'cost_per_query' in summary
                })
                
                cost_info = f", Cost: ${cost_per_query:.4f}" if cost_per_query > 0 else ", Cost: N/A"
                print(f"Processed {run_dir}: {model_id}, Success Rate: {success_rate:.3f}, Avg Time: {avg_time_per_query:.2f}s{cost_info}")
                
            except Exception as e:
                print(f"Error processing {json_file}: {e}")
    
    return data

def group_by_model(data):
    """Group data by model and calculate statistics."""
    grouped = defaultdict(list)
    
    for entry in data:
        grouped[entry['model']].append(entry)
    
    stats = {}
    for model, entries in grouped.items():
        success_rates = [e['success_rate'] for e in entries]
        avg_times = [e['avg_time_per_query'] for e in entries]
        cost_per_queries = [e['cost_per_query'] for e in entries if e['has_cost_data']]
        
        stats[model] = {
            'success_rate_mean': np.mean(success_rates),
            'success_rate_std': np.std(success_rates, ddof=1) if len(success_rates) > 1 else 0,
            'avg_time_mean': np.mean(avg_times),
            'avg_time_std': np.std(avg_times, ddof=1) if len(avg_times) > 1 else 0,
            'cost_per_query_mean': np.mean(cost_per_queries) if cost_per_queries else 0.0,
            'cost_per_query_std': np.std(cost_per_queries, ddof=1) if len(cost_per_queries) > 1 else 0,
            'has_cost_data': len(cost_per_queries) > 0,
            'num_runs': len(entries),
            'num_runs_with_cost': len(cost_per_queries),
            'runs': [e['run_id'] for e in entries],
            'individual_runs': entries  # Keep individual run data for plotting
        }
    
    return stats

def create_plot(stats):
    """Create dual subplot: top shows individual runs, bottom shows mean/std with error bars."""
    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(14, 16), sharex=False)  # Don't share X to allow independent formatting
    
    # Colors for different models
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    
    # Track models with and without cost data
    models_with_cost = []
    models_without_cost = []
    
    # Calculate maximum extent of all individual runs for scaling
    all_individual_runs = []
    for model, data in stats.items():
        all_individual_runs.extend(data['individual_runs'])
    
    # Get ranges from all individual runs
    time_values = [run['avg_time_per_query'] for run in all_individual_runs]
    cost_values = [run['cost_per_query'] for run in all_individual_runs if run['has_cost_data'] and run['cost_per_query'] > 0]
    success_values = [run['success_rate'] for run in all_individual_runs]
    
    # Calculate ranges with padding
    min_time = min(time_values) if time_values else 0
    max_time = max(time_values) if time_values else 1
    min_cost = min(cost_values) if cost_values else 0
    max_cost = max(cost_values) if cost_values else 1
    min_success = min(success_values) if success_values else 0
    max_success = max(success_values) if success_values else 1
    
    # Add 30% padding
    time_range = max_time - min_time
    cost_range = max_cost - min_cost
    success_range = max_success - min_success
    
    time_padding = time_range * 0.3 if time_range > 0 else 0.3
    cost_padding = cost_range * 0.3 if cost_range > 0 else 0.003
    success_padding = success_range * 0.3 if success_range > 0 else 0.15
    
    # Create normalized scales for both subplots
    time_scale_factor = 1.0 / (time_range + 2 * time_padding) if (time_range + 2 * time_padding) > 0 else 1.0
    cost_scale_factor = -1.0 / (cost_range + 2 * cost_padding) if (cost_range + 2 * cost_padding) > 0 else -1.0
    
    # ===== TOP SUBPLOT: INDIVIDUAL RUNS =====
    for i, (model, data) in enumerate(stats.items()):
        color = colors[i % len(colors)]
        model_name = model.split('/')[-1]
        
        # Plot individual time runs (positive region) - use ACTUAL individual success rates
        for j, run in enumerate(data['individual_runs']):
            # Use the ACTUAL success rate from this individual run
            actual_success_rate = run['success_rate']
            normalized_time = ((run['avg_time_per_query'] - min_time + time_padding) * time_scale_factor)
            ax_top.scatter(
                actual_success_rate,  # Use actual individual success rate, not mean!
                normalized_time,
                color=color,
                s=80,  # Larger dots for individual plot
                alpha=0.7,
                marker='o',
                label=model_name if j == 0 else None  # Only label first occurrence
            )
        
        # Plot individual cost runs (negative region) 
        for j, run in enumerate(data['individual_runs']):
            if run['has_cost_data'] and run['cost_per_query'] > 0:
                actual_success_rate = run['success_rate']  # Use actual individual success rate
                normalized_cost = ((run['cost_per_query'] - min_cost + cost_padding) * cost_scale_factor)
                ax_top.scatter(
                    actual_success_rate,  # Use actual individual success rate, not mean!
                    normalized_cost,
                    color=color,
                    s=80,  # Larger dots
                    alpha=0.7,
                    marker='s'  # Square for cost
                )
    
    # Customize top subplot
    ax_top.set_xlabel('Success Rate (Accuracy)', fontsize=12)
    ax_top.set_ylabel('Performance Metrics (Individual Runs)', fontsize=12)
    ax_top.set_title('Individual Benchmark Runs\n(Circles = Time, Squares = Cost)', fontsize=14)
    ax_top.grid(True, alpha=0.3)
    ax_top.set_xlim(min_success - success_padding, max_success + success_padding)
    
    # Calculate proper Y-axis limits for normalized data
    max_normalized_time = 1.0  # This is the maximum normalized time value
    min_normalized_cost = -1.0  # This is the minimum normalized cost value
    ax_top.set_ylim(min_normalized_cost - 0.1, max_normalized_time + 0.1)
    
    # Add horizontal line and region labels for top plot
    ax_top.axhline(y=0, color='black', linestyle='-', alpha=0.8, linewidth=2)
    ax_top.text(0.02, 0.8, 'TIME PER QUERY', transform=ax_top.transAxes, 
                fontsize=10, alpha=0.8, weight='bold', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
    if cost_values:
        ax_top.text(0.02, 0.1, 'COST PER QUERY', transform=ax_top.transAxes, 
                    fontsize=10, alpha=0.8, weight='bold',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.5))
    
    # Add Y-axis labels to top plot
    time_ticks = [0.2, 0.4, 0.6, 0.8, 1.0]
    cost_ticks = [-0.2, -0.4, -0.6, -0.8, -1.0]
    
    time_tick_labels = []
    for tick in time_ticks:
        actual_time = (tick / time_scale_factor) + min_time - time_padding
        time_tick_labels.append(f"{actual_time:.1f}s")
    
    cost_tick_labels = []
    if cost_values:
        for tick in cost_ticks:
            actual_cost = (abs(tick) / abs(cost_scale_factor)) + min_cost - cost_padding
            cost_tick_labels.append(f"${actual_cost:.4f}")
    
    # Set custom ticks and labels for top plot
    all_ticks = [0] + time_ticks + cost_ticks
    all_labels = ['0'] + time_tick_labels + cost_tick_labels
    ax_top.set_yticks(all_ticks)
    ax_top.set_yticklabels(all_labels)
    
    # ===== BOTTOM SUBPLOT: MEAN/STD WITH ERROR BARS =====
    for i, (model, data) in enumerate(stats.items()):
        color = colors[i % len(colors)]
        success_rate = data['success_rate_mean']
        success_rate_std = data['success_rate_std']
        model_name = model.split('/')[-1]
        
        # Plot time mean with error bars (positive region)
        normalized_time = ((data['avg_time_mean'] - min_time + time_padding) * time_scale_factor)
        normalized_time_std = (data['avg_time_std'] * time_scale_factor)
        
        ax_bottom.errorbar(
            success_rate, 
            normalized_time,
            xerr=success_rate_std,
            yerr=normalized_time_std,
            fmt='o',
            color=color,
            markersize=8,
            capsize=4,
            capthick=1.5,
            label=f"{model_name} - Time (n={data['num_runs']})",
            alpha=0.8
        )
        
        # Add time annotation
        ax_bottom.annotate(
            f"{model_name}\n({data['avg_time_mean']:.1f}s)",
            (success_rate, normalized_time),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=8,
            alpha=0.7,
            color=color
        )
        
        # Plot cost mean with error bars (negative region)
        if data['has_cost_data'] and data['cost_per_query_mean'] > 0:
            models_with_cost.append(model)
            normalized_cost = ((data['cost_per_query_mean'] - min_cost + cost_padding) * cost_scale_factor)
            normalized_cost_std = (data['cost_per_query_std'] * abs(cost_scale_factor))
            
            ax_bottom.errorbar(
                success_rate,
                normalized_cost,
                xerr=success_rate_std,
                yerr=normalized_cost_std,
                fmt='s',  # Square markers for cost
                color=color,
                markersize=8,
                capsize=4,
                capthick=1.5,
                label=f"{model_name} - Cost (n={data['num_runs_with_cost']})",
                alpha=0.8,
                linestyle='--'
            )
            
            # Add cost annotation
            ax_bottom.annotate(
                f"${data['cost_per_query_mean']:.4f}",
                (success_rate, normalized_cost),
                xytext=(5, -15),
                textcoords='offset points',
                fontsize=8,
                alpha=0.7,
                color=color
            )
        else:
            models_without_cost.append(model)
    
    # Customize bottom subplot
    ax_bottom.set_xlabel('Success Rate (Accuracy)', fontsize=12)
    ax_bottom.set_ylabel('Performance Metrics (Mean ± Std)', fontsize=12)
    ax_bottom.set_title('Statistical Summary with Error Bars\n(30% Padding Beyond Error Bar Extents)', fontsize=14)
    ax_bottom.grid(True, alpha=0.3)
    ax_bottom.set_xlim(min_success - success_padding, max_success + success_padding)
    ax_bottom.set_ylim(min_normalized_cost - 0.1, max_normalized_time + 0.1)
    
    # Add horizontal line and region labels for bottom plot
    ax_bottom.axhline(y=0, color='black', linestyle='-', alpha=0.8, linewidth=2)
    ax_bottom.text(0.02, 0.8, 'TIME PER QUERY', transform=ax_bottom.transAxes, 
                   fontsize=10, alpha=0.8, weight='bold', 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
    if cost_values:
        ax_bottom.text(0.02, 0.1, 'COST PER QUERY', transform=ax_bottom.transAxes, 
                       fontsize=10, alpha=0.8, weight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.5))
    
    # Create custom Y-axis labels for bottom plot
    time_ticks = [0.2, 0.4, 0.6, 0.8, 1.0]
    cost_ticks = [-0.2, -0.4, -0.6, -0.8, -1.0]
    
    time_tick_labels = []
    for tick in time_ticks:
        actual_time = (tick / time_scale_factor) + min_time - time_padding
        time_tick_labels.append(f"{actual_time:.1f}s")
    
    cost_tick_labels = []
    if cost_values:
        for tick in cost_ticks:
            actual_cost = (abs(tick) / abs(cost_scale_factor)) + min_cost - cost_padding
            cost_tick_labels.append(f"${actual_cost:.4f}")
    
    # Set custom ticks and labels for bottom plot
    all_ticks = [0] + time_ticks + cost_ticks
    all_labels = ['0'] + time_tick_labels + cost_tick_labels
    ax_bottom.set_yticks(all_ticks)
    ax_bottom.set_yticklabels(all_labels)
    
    # Add legends
    ax_top.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    ax_bottom.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('src/applications/als_assistant/benchmarks/pv_finder/model_performance_comparison.png', dpi=300, bbox_inches='tight')
    
    # Only show plot if in interactive environment
    try:
        plt.show()
    except Exception:
        print("Plot saved (display not available in current environment)")

def create_timeline_plot(data):
    """Create timeline plot showing success rate vs wall clock time."""
    plt.figure(figsize=(16, 8))
    
    # Colors for different models
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    model_colors = {}
    
    # Sort data by timestamp
    sorted_data = sorted(data, key=lambda x: x['timestamp'])
    
    # Get unique models and assign colors
    unique_models = list(set(d['model'] for d in data))
    for i, model in enumerate(unique_models):
        model_colors[model] = colors[i % len(colors)]
    
    # Track which models we've added to legend
    models_in_legend = set()
    
    # Plot each run
    for entry in sorted_data:
        model = entry['model']
        model_name = model.split('/')[-1]
        timestamp = entry['timestamp']
        success_rate = entry['success_rate']
        
        # Only add to legend if this model hasn't been added yet
        label = model_name if model not in models_in_legend else None
        if label:
            models_in_legend.add(model)
        
        plt.scatter(
            timestamp,
            success_rate,
            color=model_colors[model],
            s=100,
            alpha=0.7,
            label=label
        )
        
        # Add annotation with run details
        plt.annotate(
            f"{model_name}\n{success_rate:.3f}",
            (timestamp, success_rate),
            xytext=(5, 5),
            textcoords='offset points',
            fontsize=8,
            alpha=0.8,
            color=model_colors[model]
        )
    
    # Customize the plot
    plt.xlabel('Wall Clock Time (When Test Was Performed)', fontsize=12)
    plt.ylabel('Success Rate (Accuracy)', fontsize=12)
    plt.title('Model Performance Over Time\n(Success Rate vs Wall Clock Time)', fontsize=14)
    plt.grid(True, alpha=0.3)
    
    # Format x-axis for datetime display
    ax = plt.gca()
    
    # Calculate time span to choose appropriate formatting
    time_span = max(entry['timestamp'] for entry in sorted_data) - min(entry['timestamp'] for entry in sorted_data)
    
    if time_span.days > 1:
        # Multi-day span: show date and time
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d\n%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    else:
        # Single day: show just time
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    
    plt.xticks(rotation=45)
    
    # Set y-axis to show full range
    plt.ylim(0, 1.05)
    
    # Add legend
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('src/applications/als_assistant/benchmarks/pv_finder/performance_timeline.png', dpi=300, bbox_inches='tight')
    
    # Only show plot if in interactive environment
    try:
        plt.show()
    except Exception:
        print("Timeline plot saved (display not available in current environment)")

def print_summary_table(stats):
    """Print a summary table of the results."""
    print("\n" + "="*100)
    print("BENCHMARK RESULTS SUMMARY")
    print("="*100)
    print(f"{'Model':<25} {'Runs':<5} {'Accuracy':<15} {'Time (s)':<15} {'Cost ($)':<15} {'Runs List'}")
    print("-"*100)
    
    # Sort by accuracy (descending)
    sorted_models = sorted(stats.items(), key=lambda x: x[1]['success_rate_mean'], reverse=True)
    
    for model, data in sorted_models:
        accuracy_str = f"{data['success_rate_mean']:.3f} ± {data['success_rate_std']:.3f}"
        time_str = f"{data['avg_time_mean']:.1f} ± {data['avg_time_std']:.1f}"
        
        # Cost string with fallback for missing data
        if data['has_cost_data']:
            cost_str = f"{data['cost_per_query_mean']:.4f} ± {data['cost_per_query_std']:.4f}"
        else:
            cost_str = "No cost data"
        
        runs_str = ", ".join(data['runs'])
        
        print(f"{model:<25} {data['num_runs']:<5} {accuracy_str:<15} {time_str:<15} {cost_str:<15} {runs_str}")
    
    print("="*100)
    
    # Print additional cost summary if any models have cost data
    models_with_cost = [model for model, data in stats.items() if data['has_cost_data']]
    if models_with_cost:
        print(f"\nCOST ANALYSIS ({len(models_with_cost)} models with cost data):")
        print("-" * 60)
        for model in sorted(models_with_cost, key=lambda x: stats[x]['cost_per_query_mean']):
            data = stats[model]
            print(f"{model.split('/')[-1]:<25} ${data['cost_per_query_mean']:.4f} per query")
        print("-" * 60)

def main():
    """Main function."""
    # Path to benchmark runs directory
    base_dir = 'src/applications/als_assistant/benchmarks/pv_finder/benchmark_runs'
    
    print("Reading benchmark data...")
    data = read_benchmark_data(base_dir)
    
    if not data:
        print("No benchmark data found!")
        return
    
    print(f"\nFound {len(data)} benchmark runs")
    
    # Group by model and calculate statistics
    stats = group_by_model(data)
    
    # Print summary table
    print_summary_table(stats)
    
    # Create performance comparison plot
    print("\nCreating performance comparison plot...")
    create_plot(stats)
    
    # Create timeline plot
    print("Creating timeline plot...")
    create_timeline_plot(data)
    
    print("Analysis complete!")
    print("- Performance comparison plot saved as 'model_performance_comparison.png'")
    print("- Timeline plot saved as 'performance_timeline.png'")

if __name__ == "__main__":
    main() 