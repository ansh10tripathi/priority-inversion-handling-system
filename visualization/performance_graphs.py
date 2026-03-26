"""Performance comparison graphs module for Priority Inversion Handling System."""

import matplotlib.pyplot as plt
import os


def plot_comparison_graphs(results_list, output_dir='output'):
    """
    Generate comparison graphs for multiple protocols.

    Args:
        results_list: List of (metrics, protocol_name) tuples
        output_dir: Directory to save graphs (default: 'output')
    """
    if len(results_list) < 2:
        print("Need at least 2 protocols to generate comparison graphs")
        return
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    protocols = [proto for _, proto in results_list]
    
    # Extract metrics
    waiting_times = [metrics['avg_waiting_time'] for metrics, _ in results_list]
    turnaround_times = [metrics['avg_turnaround_time'] for metrics, _ in results_list]
    context_switches = [metrics['context_switches'] for metrics, _ in results_list]
    inversion_durations = [metrics['priority_inversion_duration'] for metrics, _ in results_list]
    
    # Color scheme
    colors = ['#e74c3c', '#3498db', '#2ecc71']
    
    # Graph 1: Average Waiting Time
    plt.figure(figsize=(10, 6))
    bars = plt.bar(protocols, waiting_times, color=colors[:len(protocols)], edgecolor='black', linewidth=1.5)
    plt.xlabel('Protocol', fontsize=12, fontweight='bold')
    plt.ylabel('Average Waiting Time (time units)', fontsize=12, fontweight='bold')
    plt.title('Average Waiting Time Comparison', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar, value in zip(bars, waiting_times):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    filename = os.path.join(output_dir, 'comparison_waiting_time.png')
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")
    
    # Graph 2: Average Turnaround Time
    plt.figure(figsize=(10, 6))
    bars = plt.bar(protocols, turnaround_times, color=colors[:len(protocols)], edgecolor='black', linewidth=1.5)
    plt.xlabel('Protocol', fontsize=12, fontweight='bold')
    plt.ylabel('Average Turnaround Time (time units)', fontsize=12, fontweight='bold')
    plt.title('Average Turnaround Time Comparison', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar, value in zip(bars, turnaround_times):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.2f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    filename = os.path.join(output_dir, 'comparison_turnaround_time.png')
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")
    
    # Graph 3: Context Switches
    plt.figure(figsize=(10, 6))
    bars = plt.bar(protocols, context_switches, color=colors[:len(protocols)], edgecolor='black', linewidth=1.5)
    plt.xlabel('Protocol', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Context Switches', fontsize=12, fontweight='bold')
    plt.title('Context Switches Comparison', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar, value in zip(bars, context_switches):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{value}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    filename = os.path.join(output_dir, 'comparison_context_switches.png')
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")
    
    # Graph 4: Priority Inversion Duration
    plt.figure(figsize=(10, 6))
    bars = plt.bar(protocols, inversion_durations, color=colors[:len(protocols)], edgecolor='black', linewidth=1.5)
    plt.xlabel('Protocol', fontsize=12, fontweight='bold')
    plt.ylabel('Priority Inversion Duration (time units)', fontsize=12, fontweight='bold')
    plt.title('Priority Inversion Duration Comparison', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    
    for bar, value in zip(bars, inversion_durations):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{value}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    filename = os.path.join(output_dir, 'comparison_inversion_duration.png')
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {filename}")
