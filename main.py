"""Main module for Priority Inversion Handling System demonstration."""

import argparse
import json
import csv
import sys
import os

from models import Task
from scheduler import Mutex
from simulation import Simulation, print_metrics_report, compare_protocols, export_metrics_to_csv
from visualization import plot_gantt_chart, visualize_all_protocols, plot_comparison_graphs
from utils import TaskGenerator, generate_random_tasks, generate_inversion_scenario, export_results, export_comparison, export_to_json


def create_tasks():
    """Create example tasks for demonstration."""
    return [
        Task(task_id='L', priority=1, arrival_time=0, execution_time=3, needs_resource=True),
        Task(task_id='H', priority=3, arrival_time=1, execution_time=2, needs_resource=True),
        Task(task_id='M', priority=2, arrival_time=2, execution_time=3, needs_resource=False)
    ]


def load_tasks_from_json(filepath):
    """Load tasks from JSON configuration file."""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    tasks = []
    for task_data in data['tasks']:
        task = Task(
            task_id=task_data['task_id'],
            priority=task_data['priority'],
            arrival_time=task_data['arrival_time'],
            execution_time=task_data['execution_time'],
            needs_resource=task_data.get('needs_resource', False)
        )
        tasks.append(task)
    
    ceiling = data.get('ceiling_priority', None)
    return tasks, ceiling


def export_results_to_csv(results, tasks, filename):
    """Export simulation results to CSV file."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Protocol', results['protocol']])
        writer.writerow(['Total Time', results['metrics']['total_time']])
        writer.writerow(['Avg Waiting Time', f"{results['metrics']['avg_waiting_time']:.2f}"])
        writer.writerow(['Avg Turnaround Time', f"{results['metrics']['avg_turnaround_time']:.2f}"])
        writer.writerow([])
        
        # Write task details
        writer.writerow(['Task ID', 'Priority', 'Arrival', 'Execution', 'Waiting Time', 'Turnaround Time'])
        for task in tasks:
            writer.writerow([
                task.task_id,
                task.original_priority,
                task.arrival_time,
                task.execution_time,
                task.get_waiting_time(task.finish_time),
                task.get_turnaround_time()
            ])
    
    print(f"Results exported to: {filename}")


def print_timeline(timeline):
    """Print execution timeline."""
    print("\nExecution Timeline:")
    for time, task_id in timeline:
        task_str = f"Task {task_id}" if task_id else "IDLE"
        print(f"  Time {time}: {task_str}")


def print_task_metrics(tasks):
    """Print individual task metrics."""
    print("\nTask Metrics:")
    for task in tasks:
        print(f"  Task {task.task_id}:")
        print(f"    Waiting Time: {task.get_waiting_time(task.finish_time)}")
        print(f"    Turnaround Time: {task.get_turnaround_time()}")


def run_simulation(protocol, tasks=None, ceiling_priority=None, verbose=True, realtime=False, delay=1.0, interactive=False):
    """Run simulation with specified protocol."""
    if verbose and not realtime:
        print(f"\n{'='*60}")
        print(f"Running Simulation: {protocol} Protocol")
        print(f"{'='*60}")
    
    if tasks is None:
        tasks = create_tasks()
        ceiling_priority = 3 if protocol == 'PCP' else None
    
    mutex = Mutex(ceiling_priority=ceiling_priority)
    sim = Simulation(tasks, mutex, protocol, realtime=realtime, delay=delay, interactive=interactive)
    results = sim.run()
    
    if verbose and not realtime:
        print_timeline(results['timeline'])
        print_task_metrics(tasks)
    
    return results, tasks


def run_cli():
    """Run with command line interface."""
    parser = argparse.ArgumentParser(
        description='Priority Inversion Handling System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python main.py --protocol pip
  python main.py --protocol pcp --visualize
  python main.py --tasks config.json --protocol pip --export results.csv
  python main.py --generate 5 --protocol pip --visualize
  python main.py --generate 8 --max-priority 10 --resource-prob 0.7 --protocol pcp
  python main.py --generate 5 --inversion-scenario --compare --visualize
  python main.py --protocol pip --metrics-report
  python main.py --compare --metrics-report --visualize
  python main.py --protocol pcp --metrics-csv detailed_metrics.csv
        """
    )
    
    parser.add_argument(
        '--protocol',
        choices=['none', 'pip', 'pcp'],
        default='none',
        help='Scheduling protocol to use (default: none)'
    )
    
    parser.add_argument(
        '--tasks',
        type=str,
        metavar='FILE',
        help='Load tasks from JSON configuration file'
    )
    
    parser.add_argument(
        '--generate',
        type=int,
        metavar='N',
        help='Generate N random tasks automatically'
    )
    
    parser.add_argument(
        '--max-priority',
        type=int,
        default=5,
        metavar='P',
        help='Maximum priority for generated tasks (default: 5)'
    )
    
    parser.add_argument(
        '--max-execution',
        type=int,
        default=10,
        metavar='T',
        help='Maximum execution time for generated tasks (default: 10)'
    )
    
    parser.add_argument(
        '--resource-prob',
        type=float,
        default=0.5,
        metavar='P',
        help='Probability (0.0-1.0) that a task needs resource (default: 0.5)'
    )
    
    parser.add_argument(
        '--inversion-scenario',
        action='store_true',
        help='Generate tasks with guaranteed priority inversion scenario'
    )
    
    parser.add_argument(
        '--visualize',
        action='store_true',
        help='Generate Gantt chart visualization'
    )
    
    parser.add_argument(
        '--export',
        type=str,
        metavar='FILE',
        help='Export simulation results to CSV file'
    )
    
    parser.add_argument(
        '--export-json',
        type=str,
        metavar='FILE',
        help='Export simulation results to JSON file'
    )
    
    parser.add_argument(
        '--export-all',
        action='store_true',
        help='Export results to both CSV and JSON (results_<protocol>.csv/json)'
    )
    
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare all three protocols'
    )
    
    parser.add_argument(
        '--metrics-report',
        action='store_true',
        help='Display detailed metrics report'
    )
    
    parser.add_argument(
        '--metrics-csv',
        type=str,
        metavar='FILE',
        help='Export detailed metrics to CSV file'
    )
    
    parser.add_argument(
        '--realtime',
        action='store_true',
        help='Enable real-time step-by-step simulation with visual display'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=1.0,
        metavar='SECONDS',
        help='Delay between time steps in realtime mode (default: 1.0 seconds)'
    )

    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Step-by-step mode: press ENTER to advance each time step (implies --realtime)'
    )
    
    args = parser.parse_args()

    # --interactive implies --realtime
    if args.interactive:
        args.realtime = True
    
    # Determine protocol name
    protocol_map = {'none': 'None', 'pip': 'PIP', 'pcp': 'PCP'}
    protocol = protocol_map[args.protocol]
    
    # Load or generate tasks
    tasks = None
    ceiling_priority = None
    
    if args.tasks:
        print(f"Loading tasks from: {args.tasks}")
        tasks, ceiling_priority = load_tasks_from_json(args.tasks)
        print(f"Loaded {len(tasks)} tasks")
    elif args.generate:
        print(f"Generating {args.generate} random tasks...")
        
        if args.inversion_scenario:
            print("Using priority inversion scenario generator")
            tasks = generate_inversion_scenario(
                count=args.generate,
                max_priority=args.max_priority,
                max_execution_time=args.max_execution
            )
        else:
            generator = TaskGenerator(
                number_of_tasks=args.generate,
                max_priority=args.max_priority,
                max_execution_time=args.max_execution,
                max_arrival_time=args.max_execution // 2,
                resource_probability=args.resource_prob
            )
            tasks = generator.generate()
        
        ceiling_priority = max(t.priority for t in tasks) if protocol == 'PCP' else None
        print(f"Generated {len(tasks)} tasks")
        print(f"Configuration: max_priority={args.max_priority}, "
              f"max_execution={args.max_execution}, resource_prob={args.resource_prob}")
    
    # Print task configuration
    if tasks:
        print("\nTask Configuration:")
        for task in tasks:
            resource_str = "Needs Resource" if task.needs_resource else "No Resource"
            print(f"  Task {task.task_id}: Priority={task.priority}, "
                  f"Arrival={task.arrival_time}, Execution={task.execution_time}, {resource_str}")
    
    # Run simulation
    print(f"\n{'='*60}")
    print(f"Priority Inversion Handling System")
    print(f"{'='*60}")
    
    if args.interactive:
        print(f"\n[INTERACTIVE] Step-by-step mode enabled. Press ENTER to advance each step.")
    elif args.realtime:
        print(f"\n[REALTIME] Real-Time Mode Enabled (Delay: {args.delay}s per step)")
        print(f"Watch the simulation execute step-by-step...\n")
    
    if args.compare:
        # Run all three protocols
        results_list = []
        for proto in ['None', 'PIP', 'PCP']:
            # Create fresh task copies for each simulation
            if args.tasks:
                task_set, ceiling = load_tasks_from_json(args.tasks)
            elif args.generate:
                if args.inversion_scenario:
                    task_set = generate_inversion_scenario(
                        count=args.generate,
                        max_priority=args.max_priority,
                        max_execution_time=args.max_execution
                    )
                else:
                    generator = TaskGenerator(
                        number_of_tasks=args.generate,
                        max_priority=args.max_priority,
                        max_execution_time=args.max_execution,
                        max_arrival_time=args.max_execution // 2,
                        resource_probability=args.resource_prob
                    )
                    task_set = generator.generate()
            else:
                task_set = create_tasks()
            
            ceiling = ceiling_priority if proto == 'PCP' else None
            results, task_set = run_simulation(proto, task_set, ceiling, verbose=not args.realtime,
                                               realtime=args.realtime, delay=args.delay, interactive=args.interactive)
            results_list.append((results, task_set, proto))
        
        # Print comparison
        print(f"\n{'='*60}")
        print("Comparison Summary")
        print(f"{'='*60}")
        print(f"\n{'Protocol':<20} {'Total Time':<15} {'Avg Wait':<15} {'Avg Turnaround':<15}")
        print("-" * 60)
        
        for results, _, proto in results_list:
            metrics = results['metrics']
            print(f"{proto:<20} {metrics['total_time']:<15} "
                  f"{metrics['avg_waiting_time']:<15.2f} "
                  f"{metrics['avg_turnaround_time']:<15.2f}")
        
        # Detailed comparison report
        if args.metrics_report:
            comparison_report = compare_protocols([
                (results['metrics'], proto) for results, _, proto in results_list
            ])
            print(comparison_report)
        
        # Generate comparison graphs
        print(f"\n{'='*60}")
        print("Generating Comparison Graphs...")
        print(f"{'='*60}")
        plot_comparison_graphs([
            (results['metrics'], proto) for results, _, proto in results_list
        ], output_dir='output')
        
        # Visualize all if requested
        if args.visualize:
            print(f"\n{'='*60}")
            print("Generating Gantt Charts...")
            print(f"{'='*60}")
            visualize_all_protocols([
                (results['timeline'], tasks, proto)
                for results, tasks, proto in results_list
            ], output_dir='output')
        
        # Export comparison if requested
        if args.export_all:
            print(f"\n{'='*60}")
            print("Exporting Comparison Results...")
            print(f"{'='*60}")
            export_comparison(results_list, output_dir='output')
    else:
        # Run single protocol
        results, tasks = run_simulation(protocol, tasks, ceiling_priority, verbose=not args.realtime,
                                        realtime=args.realtime, delay=args.delay, interactive=args.interactive)
        
        # Display detailed metrics if requested
        if args.metrics_report:
            print_metrics_report(results['metrics'], protocol)
        
        # Visualize if requested
        if args.visualize:
            print(f"\nGenerating Gantt chart...")
            plot_gantt_chart(results['timeline'], tasks, protocol, output_dir='output')
        
        # Export if requested
        if args.export:
            export_results_to_csv(results, tasks, os.path.join('output', args.export))
        
        # Export to JSON if requested
        if args.export_json:
            export_to_json(results, tasks, os.path.join('output', args.export_json))
        
        # Export to both formats if requested
        if args.export_all:
            export_results(results, tasks, protocol, output_dir='output')
        
        # Export detailed metrics if requested
        if args.metrics_csv:
            export_metrics_to_csv(results['metrics'], tasks, protocol, os.path.join('output', args.metrics_csv))


def main():
    """Run all simulations and compare results (legacy mode)."""
    print("\n" + "="*60)
    print("Priority Inversion Handling System Demonstration")
    print("="*60)
    print("\nTask Configuration:")
    print("  Task L: Priority=1, Arrival=0, Execution=3, Needs Resource")
    print("  Task H: Priority=3, Arrival=1, Execution=2, Needs Resource")
    print("  Task M: Priority=2, Arrival=2, Execution=3, No Resource")
    
    # Run simulations with different protocols
    results_none, tasks_none = run_simulation('None')
    results_pip, tasks_pip = run_simulation('PIP')
    results_pcp, tasks_pcp = run_simulation('PCP')
    
    # Compare results
    print(f"\n{'='*60}")
    print("Comparison Summary")
    print(f"{'='*60}")
    print(f"\n{'Protocol':<20} {'Total Time':<15} {'Avg Wait':<15} {'Avg Turnaround':<15}")
    print("-" * 60)
    
    for name, results in [('None', results_none), ('PIP', results_pip), ('PCP', results_pcp)]:
        metrics = results['metrics']
        print(f"{name:<20} {metrics['total_time']:<15} "
              f"{metrics['avg_waiting_time']:<15.2f} "
              f"{metrics['avg_turnaround_time']:<15.2f}")
    
    # Generate Gantt charts
    print(f"\n{'='*60}")
    print("Generating Gantt Charts...")
    print(f"{'='*60}")
    visualize_all_protocols([
        (results_none['timeline'], tasks_none, 'None'),
        (results_pip['timeline'], tasks_pip, 'PIP'),
        (results_pcp['timeline'], tasks_pcp, 'PCP')
    ], output_dir='output')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_cli()
    else:
        main()
