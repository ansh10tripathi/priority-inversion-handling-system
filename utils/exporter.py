"""Exporter module for Priority Inversion Handling System."""

import csv
import json
import os


def export_to_csv(results, tasks, filename):
    """
    Export simulation results to CSV format.

    Args:
        results: Dictionary containing timeline, metrics, and protocol
        tasks: List of Task objects
        filename: Output CSV filename
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow(['Priority Inversion Handling System - Simulation Results'])
        writer.writerow([])
        
        # Protocol information
        writer.writerow(['Protocol', results['protocol']])
        writer.writerow([])
        
        # Overall metrics
        writer.writerow(['Overall Metrics'])
        writer.writerow(['Metric', 'Value'])
        metrics = results['metrics']
        writer.writerow(['Total Time', metrics['total_time']])
        writer.writerow(['Average Waiting Time', f"{metrics['avg_waiting_time']:.2f}"])
        writer.writerow(['Average Turnaround Time', f"{metrics['avg_turnaround_time']:.2f}"])
        writer.writerow(['Average Response Time', f"{metrics['avg_response_time']:.2f}"])
        writer.writerow(['CPU Utilization (%)', f"{metrics['cpu_utilization']:.2f}"])
        writer.writerow(['Context Switches', metrics['context_switches']])
        writer.writerow(['Priority Inversion Count', metrics['priority_inversion_count']])
        writer.writerow(['Priority Inversion Duration', metrics['priority_inversion_duration']])
        writer.writerow(['Throughput', f"{metrics['throughput']:.4f}"])
        writer.writerow([])
        
        # Task metrics
        writer.writerow(['Task Metrics'])
        writer.writerow(['Task ID', 'Priority', 'Arrival Time', 'Execution Time', 
                        'Start Time', 'Finish Time', 'Waiting Time', 'Turnaround Time', 'Response Time'])
        
        for task in tasks:
            response_time = task.start_time - task.arrival_time if task.start_time is not None else 0
            writer.writerow([
                task.task_id,
                task.original_priority,
                task.arrival_time,
                task.execution_time,
                task.start_time if task.start_time is not None else 'N/A',
                task.finish_time if task.finish_time is not None else 'N/A',
                task.get_waiting_time(task.finish_time),
                task.get_turnaround_time(),
                response_time
            ])
        
        writer.writerow([])
        
        # Execution timeline
        writer.writerow(['Execution Timeline'])
        writer.writerow(['Time', 'Task ID'])
        for time, task_id in results['timeline']:
            writer.writerow([time, task_id if task_id else 'IDLE'])
    
    print(f"Results exported to CSV: {filename}")


def export_to_json(results, tasks, filename):
    """
    Export simulation results to JSON format.

    Args:
        results: Dictionary containing timeline, metrics, and protocol
        tasks: List of Task objects
        filename: Output JSON filename
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    # Build JSON structure
    data = {
        'protocol': results['protocol'],
        'metrics': {
            'total_time': results['metrics']['total_time'],
            'avg_waiting_time': round(results['metrics']['avg_waiting_time'], 2),
            'avg_turnaround_time': round(results['metrics']['avg_turnaround_time'], 2),
            'avg_response_time': round(results['metrics']['avg_response_time'], 2),
            'cpu_utilization': round(results['metrics']['cpu_utilization'], 2),
            'context_switches': results['metrics']['context_switches'],
            'priority_inversion_count': results['metrics']['priority_inversion_count'],
            'priority_inversion_duration': results['metrics']['priority_inversion_duration'],
            'throughput': round(results['metrics']['throughput'], 4)
        },
        'tasks': [],
        'timeline': []
    }
    
    # Add task information
    for task in tasks:
        response_time = task.start_time - task.arrival_time if task.start_time is not None else 0
        task_data = {
            'task_id': task.task_id,
            'priority': task.original_priority,
            'arrival_time': task.arrival_time,
            'execution_time': task.execution_time,
            'start_time': task.start_time,
            'finish_time': task.finish_time,
            'waiting_time': task.get_waiting_time(task.finish_time),
            'turnaround_time': task.get_turnaround_time(),
            'response_time': response_time,
            'needs_resource': task.needs_resource
        }
        data['tasks'].append(task_data)
    
    # Add timeline
    for time, task_id in results['timeline']:
        data['timeline'].append({
            'time': time,
            'task_id': task_id if task_id else None
        })
    
    # Write to file
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Results exported to JSON: {filename}")


def export_results(results, tasks, protocol_name, output_dir='output', formats=['csv', 'json']):
    """
    Export simulation results to multiple formats.

    Args:
        results: Dictionary containing timeline, metrics, and protocol
        tasks: List of Task objects
        protocol_name: Name of the protocol
        output_dir: Directory to save files (default: current directory)
        formats: List of formats to export ('csv', 'json')
    """
    # Create output directory if it doesn't exist
    if output_dir != '.' and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Generate base filename
    base_filename = f"results_{protocol_name.lower()}"
    
    # Export to requested formats
    if 'csv' in formats:
        csv_filename = os.path.join(output_dir, f"{base_filename}.csv")
        export_to_csv(results, tasks, csv_filename)
    
    if 'json' in formats:
        json_filename = os.path.join(output_dir, f"{base_filename}.json")
        export_to_json(results, tasks, json_filename)


def export_comparison(results_list, output_dir='output'):
    """
    Export comparison of multiple protocols to CSV and JSON.

    Args:
        results_list: List of (results, tasks, protocol_name) tuples
        output_dir: Directory to save files
    """
    # CSV comparison
    csv_filename = os.path.join(output_dir, 'comparison_summary.csv')
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(csv_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        
        writer.writerow(['Protocol Comparison Summary'])
        writer.writerow([])
        
        # Header
        header = ['Metric'] + [proto for _, _, proto in results_list]
        writer.writerow(header)
        
        # Metrics
        metrics_to_compare = [
            ('Total Time', 'total_time'),
            ('Avg Waiting Time', 'avg_waiting_time'),
            ('Avg Turnaround Time', 'avg_turnaround_time'),
            ('Avg Response Time', 'avg_response_time'),
            ('CPU Utilization (%)', 'cpu_utilization'),
            ('Context Switches', 'context_switches'),
            ('Inversion Count', 'priority_inversion_count'),
            ('Inversion Duration', 'priority_inversion_duration'),
            ('Throughput', 'throughput')
        ]
        
        for label, key in metrics_to_compare:
            row = [label]
            for results, _, _ in results_list:
                value = results['metrics'][key]
                if isinstance(value, float):
                    row.append(f"{value:.2f}")
                else:
                    row.append(value)
            writer.writerow(row)
    
    print(f"Comparison exported to CSV: {csv_filename}")
    
    # JSON comparison
    json_filename = os.path.join(output_dir, 'comparison_summary.json')
    comparison_data = {
        'protocols': []
    }
    
    for results, tasks, proto in results_list:
        protocol_data = {
            'name': proto,
            'metrics': {
                'total_time': results['metrics']['total_time'],
                'avg_waiting_time': round(results['metrics']['avg_waiting_time'], 2),
                'avg_turnaround_time': round(results['metrics']['avg_turnaround_time'], 2),
                'avg_response_time': round(results['metrics']['avg_response_time'], 2),
                'cpu_utilization': round(results['metrics']['cpu_utilization'], 2),
                'context_switches': results['metrics']['context_switches'],
                'priority_inversion_count': results['metrics']['priority_inversion_count'],
                'priority_inversion_duration': results['metrics']['priority_inversion_duration'],
                'throughput': round(results['metrics']['throughput'], 4)
            }
        }
        comparison_data['protocols'].append(protocol_data)
    
    with open(json_filename, 'w') as f:
        json.dump(comparison_data, f, indent=2)
    
    print(f"Comparison exported to JSON: {json_filename}")
