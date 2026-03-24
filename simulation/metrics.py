"""Metrics module for Priority Inversion Handling System."""

import os


class MetricsCollector:
    """Collects and analyzes simulation performance metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.context_switches = 0
        self.priority_inversion_events = []
        self.previous_task = None
        self.idle_time = 0
        self.total_time = 0

    def record_context_switch(self, from_task, to_task):
        """
        Record a context switch between tasks.

        Args:
            from_task: Task being switched from (or None if idle)
            to_task: Task being switched to (or None if idle)
        """
        if from_task != to_task:
            self.context_switches += 1

    def record_priority_inversion(self, start_time, end_time, high_task, low_task):
        """
        Record a priority inversion event.

        Args:
            start_time: When inversion started
            end_time: When inversion ended
            high_task: High priority task that was blocked
            low_task: Low priority task that caused blocking
        """
        self.priority_inversion_events.append({
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time,
            'high_task': high_task.task_id,
            'high_priority': high_task.original_priority,
            'low_task': low_task.task_id,
            'low_priority': low_task.original_priority
        })

    def record_idle(self):
        """Record one time unit of CPU idle time."""
        self.idle_time += 1

    def get_priority_inversion_duration(self):
        """
        Calculate total priority inversion duration.

        Returns:
            Total time spent in priority inversion
        """
        return sum(event['duration'] for event in self.priority_inversion_events)

    def get_priority_inversion_count(self):
        """
        Get number of priority inversion events.

        Returns:
            Count of priority inversion events
        """
        return len(self.priority_inversion_events)


def calculate_metrics(tasks, total_time, metrics_collector=None):
    """
    Calculate comprehensive performance metrics.

    Args:
        tasks: List of Task objects
        total_time: Total simulation time
        metrics_collector: Optional MetricsCollector instance

    Returns:
        Dictionary containing all metrics
    """
    # Basic metrics
    waiting_times = [t.get_waiting_time(t.finish_time) for t in tasks]
    turnaround_times = [t.get_turnaround_time() for t in tasks]
    response_times = [t.start_time - t.arrival_time for t in tasks if t.start_time is not None]
    
    avg_waiting_time = sum(waiting_times) / len(tasks) if tasks else 0
    avg_turnaround_time = sum(turnaround_times) / len(tasks) if tasks else 0
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # CPU utilization
    total_execution_time = sum(t.execution_time for t in tasks)
    cpu_utilization = (total_execution_time / total_time * 100) if total_time > 0 else 0
    
    # Context switches and priority inversion
    context_switches = metrics_collector.context_switches if metrics_collector else 0
    inversion_duration = metrics_collector.get_priority_inversion_duration() if metrics_collector else 0
    inversion_count = metrics_collector.get_priority_inversion_count() if metrics_collector else 0
    
    return {
        'total_time': total_time,
        'avg_waiting_time': avg_waiting_time,
        'avg_turnaround_time': avg_turnaround_time,
        'avg_response_time': avg_response_time,
        'cpu_utilization': cpu_utilization,
        'context_switches': context_switches,
        'priority_inversion_duration': inversion_duration,
        'priority_inversion_count': inversion_count,
        'throughput': len(tasks) / total_time if total_time > 0 else 0
    }


def print_metrics_report(metrics, protocol_name):
    """
    Print a formatted metrics report.

    Args:
        metrics: Dictionary of metrics
        protocol_name: Name of the protocol
    """
    print(f"\n{'='*60}")
    print(f"Performance Metrics - {protocol_name} Protocol")
    print(f"{'='*60}")
    print(f"Total Time:                  {metrics['total_time']} time units")
    print(f"Average Waiting Time:        {metrics['avg_waiting_time']:.2f} time units")
    print(f"Average Turnaround Time:     {metrics['avg_turnaround_time']:.2f} time units")
    print(f"Average Response Time:       {metrics['avg_response_time']:.2f} time units")
    print(f"CPU Utilization:             {metrics['cpu_utilization']:.2f}%")
    print(f"Context Switches:            {metrics['context_switches']}")
    print(f"Priority Inversion Count:    {metrics['priority_inversion_count']}")
    print(f"Priority Inversion Duration: {metrics['priority_inversion_duration']} time units")
    print(f"Throughput:                  {metrics['throughput']:.4f} tasks/time unit")


def compare_protocols(results_list):
    """
    Generate a comparison report for multiple protocols.

    Args:
        results_list: List of (metrics, protocol_name) tuples

    Returns:
        Formatted comparison string
    """
    if not results_list:
        return "No results to compare"
    
    # Header
    report = f"\n{'='*100}\n"
    report += "Protocol Comparison Report\n"
    report += f"{'='*100}\n\n"
    
    # Table header
    header = f"{'Metric':<30}"
    for _, protocol in results_list:
        header += f"{protocol:>20}"
    report += header + "\n"
    report += "-" * 100 + "\n"
    
    # Metrics rows
    metrics_to_compare = [
        ('Total Time', 'total_time', ''),
        ('Avg Waiting Time', 'avg_waiting_time', '.2f'),
        ('Avg Turnaround Time', 'avg_turnaround_time', '.2f'),
        ('Avg Response Time', 'avg_response_time', '.2f'),
        ('CPU Utilization (%)', 'cpu_utilization', '.2f'),
        ('Context Switches', 'context_switches', ''),
        ('Inversion Count', 'priority_inversion_count', ''),
        ('Inversion Duration', 'priority_inversion_duration', ''),
        ('Throughput', 'throughput', '.4f')
    ]
    
    for label, key, fmt in metrics_to_compare:
        row = f"{label:<30}"
        for metrics, _ in results_list:
            value = metrics[key]
            if fmt:
                row += f"{value:>20{fmt}}"
            else:
                row += f"{value:>20}"
        report += row + "\n"
    
    # Analysis
    report += "\n" + "="*100 + "\n"
    report += "Analysis\n"
    report += "="*100 + "\n"
    
    # Find best protocol for each metric
    best_waiting = min(results_list, key=lambda x: x[0]['avg_waiting_time'])
    best_response = min(results_list, key=lambda x: x[0]['avg_response_time'])
    best_inversion = min(results_list, key=lambda x: x[0]['priority_inversion_duration'])
    
    report += f"Best Avg Waiting Time:       {best_waiting[1]} ({best_waiting[0]['avg_waiting_time']:.2f})\n"
    report += f"Best Avg Response Time:      {best_response[1]} ({best_response[0]['avg_response_time']:.2f})\n"
    report += f"Lowest Inversion Duration:   {best_inversion[1]} ({best_inversion[0]['priority_inversion_duration']})\n"
    
    return report


def export_metrics_to_csv(metrics, tasks, protocol_name, filename):
    """
    Export detailed metrics to CSV file.

    Args:
        metrics: Dictionary of metrics
        tasks: List of Task objects
        protocol_name: Name of the protocol
        filename: Output CSV filename
    """
    import csv
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Overall metrics
        writer.writerow(['Overall Metrics'])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Protocol', protocol_name])
        writer.writerow(['Total Time', metrics['total_time']])
        writer.writerow(['Avg Waiting Time', f"{metrics['avg_waiting_time']:.2f}"])
        writer.writerow(['Avg Turnaround Time', f"{metrics['avg_turnaround_time']:.2f}"])
        writer.writerow(['Avg Response Time', f"{metrics['avg_response_time']:.2f}"])
        writer.writerow(['CPU Utilization (%)', f"{metrics['cpu_utilization']:.2f}"])
        writer.writerow(['Context Switches', metrics['context_switches']])
        writer.writerow(['Priority Inversion Count', metrics['priority_inversion_count']])
        writer.writerow(['Priority Inversion Duration', metrics['priority_inversion_duration']])
        writer.writerow(['Throughput', f"{metrics['throughput']:.4f}"])
        writer.writerow([])
        
        # Per-task metrics
        writer.writerow(['Per-Task Metrics'])
        writer.writerow(['Task ID', 'Priority', 'Arrival', 'Execution', 'Start', 'Finish', 
                        'Waiting Time', 'Turnaround Time', 'Response Time'])
        
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
