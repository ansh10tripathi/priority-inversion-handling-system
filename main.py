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

# ── Canonical demo scenario ───────────────────────────────────────────────────
# Matches DEMO_TASKS in api.py, App.js, and gui/controller.py exactly.

DEMO_TASKS_CONFIG = [
    dict(task_id='L',  priority=1, arrival_time=0, execution_time=10, needs_resource=True),
    dict(task_id='H',  priority=5, arrival_time=4, execution_time=2,  needs_resource=True),
    dict(task_id='M1', priority=3, arrival_time=1, execution_time=4,  needs_resource=False),
    dict(task_id='M2', priority=4, arrival_time=2, execution_time=3,  needs_resource=False),
]


def create_tasks():
    """Create the canonical demo tasks for demonstration."""
    return [Task(**d) for d in DEMO_TASKS_CONFIG]


def _print_demo_config():
    """Print the canonical demo task configuration."""
    print("\nTask Configuration (Demo: Priority Inversion Scenario):")
    for d in DEMO_TASKS_CONFIG:
        res = "Needs Resource" if d['needs_resource'] else "No Resource"
        print(f"  Task {d['task_id']}: Priority={d['priority']}, "
              f"Arrival={d['arrival_time']}, Execution={d['execution_time']}, {res}")


# ── JSON loader ───────────────────────────────────────────────────────────────

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


# ── Export helpers ────────────────────────────────────────────────────────────

def export_results_to_csv(results, tasks, filename):
    """Export simulation results to CSV file."""
    os.makedirs(os.path.dirname(filename) or '.', exist_ok=True)
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Protocol', results['protocol']])
        writer.writerow(['Total Time', results['metrics']['total_time']])
        writer.writerow(['Avg Waiting Time', f"{results['metrics']['avg_waiting_time']:.2f}"])
        writer.writerow(['Avg Turnaround Time', f"{results['metrics']['avg_turnaround_time']:.2f}"])
        writer.writerow([])
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


# ── Display helpers ───────────────────────────────────────────────────────────

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
        print(f"    Waiting Time:    {task.get_waiting_time(task.finish_time)}")
        print(f"    Turnaround Time: {task.get_turnaround_time()}")


# ── Core simulation runner ────────────────────────────────────────────────────

def _build_ceiling(tasks, protocol):
    """Compute PCP ceiling = highest priority among resource-using tasks."""
    if protocol != 'PCP':
        return None
    resource_tasks = [t for t in tasks if t.needs_resource]
    if resource_tasks:
        return max(t.priority for t in resource_tasks)
    return max(t.priority for t in tasks)


def run_simulation(protocol, tasks=None, ceiling_priority=None,
                   verbose=True, realtime=False, delay=1.0, interactive=False):
    """Run simulation with specified protocol."""
    if verbose and not realtime:
        print(f"\n{'='*60}")
        print(f"Running Simulation: {protocol} Protocol")
        print(f"{'='*60}")

    if tasks is None:
        tasks = create_tasks()

    # Always recompute ceiling for PCP unless explicitly supplied
    if ceiling_priority is None:
        ceiling_priority = _build_ceiling(tasks, protocol)

    mutex = Mutex(ceiling_priority=ceiling_priority)
    sim = Simulation(tasks, mutex, protocol, realtime=realtime, delay=delay, interactive=interactive)
    results = sim.run()

    if verbose and not realtime:
        print_timeline(results['timeline'])
        print_task_metrics(tasks)

    return results, tasks


# ── Default (no-args) mode ────────────────────────────────────────────────────

def main():
    """Run all three protocols, compare, and generate all graphs."""
    print("\n" + "="*60)
    print("Priority Inversion Handling System — Demonstration")
    print("="*60)
    _print_demo_config()

    # Run all three protocols
    results_none, tasks_none = run_simulation('None')
    results_pip,  tasks_pip  = run_simulation('PIP')
    results_pcp,  tasks_pcp  = run_simulation('PCP')

    results_list = [
        (results_none, tasks_none, 'None'),
        (results_pip,  tasks_pip,  'PIP'),
        (results_pcp,  tasks_pcp,  'PCP'),
    ]

    # Comparison table
    print(f"\n{'='*60}")
    print("Comparison Summary")
    print(f"{'='*60}")
    print(f"\n{'Protocol':<20} {'Total Time':<15} {'Avg Wait':<15} "
          f"{'Avg Turnaround':<15} {'Inv. Duration':<15}")
    print("-" * 75)
    for results, _, proto in results_list:
        m = results['metrics']
        print(f"{proto:<20} {m['total_time']:<15} "
              f"{m['avg_waiting_time']:<15.2f} "
              f"{m['avg_turnaround_time']:<15.2f} "
              f"{m['priority_inversion_duration']:<15}")

    # Gantt charts
    print(f"\n{'='*60}")
    print("Generating Gantt Charts…")
    print(f"{'='*60}")
    visualize_all_protocols(
        [(r['timeline'], t, p) for r, t, p in results_list],
        output_dir='output'
    )

    # Comparison graphs
    print(f"\n{'='*60}")
    print("Generating Comparison Graphs…")
    print(f"{'='*60}")
    plot_comparison_graphs(
        [(r['metrics'], p) for r, _, p in results_list],
        output_dir='output'
    )

    print(f"\n{'='*60}")
    print("All outputs saved to: output/")
    print(f"{'='*60}")


# ── CLI mode ──────────────────────────────────────────────────────────────────

def run_cli():
    """Run with command line interface."""
    parser = argparse.ArgumentParser(
        description='Priority Inversion Handling System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python main.py
  python main.py --protocol pip
  python main.py --protocol pcp --visualize
  python main.py --tasks config.json --protocol pip --export results.csv
  python main.py --generate 5 --protocol pip --visualize
  python main.py --generate 8 --max-priority 10 --resource-prob 0.7 --protocol pcp
  python main.py --generate 5 --inversion-scenario --compare --visualize
  python main.py --protocol pip --metrics-report
  python main.py --compare --visualize
  python main.py --compare --metrics-report --export-all
  python main.py --protocol pcp --metrics-csv detailed_metrics.csv
  python main.py --realtime --protocol pip
  python main.py --interactive --protocol pcp
        """
    )

    parser.add_argument('--protocol', choices=['none', 'pip', 'pcp'], default='none',
                        help='Scheduling protocol to use (default: none)')
    parser.add_argument('--tasks', type=str, metavar='FILE',
                        help='Load tasks from JSON configuration file')
    parser.add_argument('--generate', type=int, metavar='N',
                        help='Generate N random tasks automatically')
    parser.add_argument('--max-priority', type=int, default=5, metavar='P',
                        help='Maximum priority for generated tasks (default: 5)')
    parser.add_argument('--max-execution', type=int, default=10, metavar='T',
                        help='Maximum execution time for generated tasks (default: 10)')
    parser.add_argument('--resource-prob', type=float, default=0.5, metavar='P',
                        help='Probability (0.0-1.0) that a task needs resource (default: 0.5)')
    parser.add_argument('--inversion-scenario', action='store_true',
                        help='Generate tasks with guaranteed priority inversion scenario')
    parser.add_argument('--visualize', action='store_true',
                        help='Generate Gantt chart visualization')
    parser.add_argument('--export', type=str, metavar='FILE',
                        help='Export simulation results to CSV file')
    parser.add_argument('--export-json', type=str, metavar='FILE',
                        help='Export simulation results to JSON file')
    parser.add_argument('--export-all', action='store_true',
                        help='Export results to both CSV and JSON')
    parser.add_argument('--compare', action='store_true',
                        help='Compare all three protocols and generate comparison graphs')
    parser.add_argument('--metrics-report', action='store_true',
                        help='Display detailed metrics report')
    parser.add_argument('--metrics-csv', type=str, metavar='FILE',
                        help='Export detailed metrics to CSV file')
    parser.add_argument('--realtime', action='store_true',
                        help='Enable real-time step-by-step simulation')
    parser.add_argument('--delay', type=float, default=1.0, metavar='SECONDS',
                        help='Delay between time steps in realtime mode (default: 1.0)')
    parser.add_argument('--interactive', action='store_true',
                        help='Press ENTER to advance each time step (implies --realtime)')

    args = parser.parse_args()

    if args.interactive:
        args.realtime = True

    protocol_map = {'none': 'None', 'pip': 'PIP', 'pcp': 'PCP'}
    protocol = protocol_map[args.protocol]

    # ── Build task set ────────────────────────────────────────────────────────

    def _make_task_set():
        """Return a fresh task list based on CLI flags."""
        if args.tasks:
            t, c = load_tasks_from_json(args.tasks)
            return t, c
        if args.generate:
            if args.inversion_scenario:
                t = generate_inversion_scenario(
                    count=args.generate,
                    max_priority=args.max_priority,
                    max_execution_time=args.max_execution
                )
            else:
                gen = TaskGenerator(
                    number_of_tasks=args.generate,
                    max_priority=args.max_priority,
                    max_execution_time=args.max_execution,
                    max_arrival_time=args.max_execution // 2,
                    resource_probability=args.resource_prob
                )
                t = gen.generate()
            return t, None
        # Default: canonical demo scenario
        return create_tasks(), None

    tasks, ceiling_priority = _make_task_set()

    # Print task configuration
    print(f"\n{'='*60}")
    print("Priority Inversion Handling System")
    print(f"{'='*60}")

    if not args.tasks and not args.generate:
        _print_demo_config()
    else:
        print("\nTask Configuration:")
        for task in tasks:
            res = "Needs Resource" if task.needs_resource else "No Resource"
            print(f"  Task {task.task_id}: Priority={task.priority}, "
                  f"Arrival={task.arrival_time}, Execution={task.execution_time}, {res}")

    if args.interactive:
        print(f"\n[INTERACTIVE] Step-by-step mode. Press ENTER to advance each step.")
    elif args.realtime:
        print(f"\n[REALTIME] Real-Time Mode (delay: {args.delay}s per step)")

    # ── Compare mode ──────────────────────────────────────────────────────────

    if args.compare:
        results_list = []
        for proto in ['None', 'PIP', 'PCP']:
            task_set, _ = _make_task_set()
            results, task_set = run_simulation(
                proto, task_set,
                verbose=not args.realtime,
                realtime=args.realtime, delay=args.delay, interactive=args.interactive
            )
            results_list.append((results, task_set, proto))

        # Comparison table
        print(f"\n{'='*60}")
        print("Comparison Summary")
        print(f"{'='*60}")
        print(f"\n{'Protocol':<20} {'Total Time':<15} {'Avg Wait':<15} "
              f"{'Avg Turnaround':<15} {'Inv. Duration':<15}")
        print("-" * 75)
        for results, _, proto in results_list:
            m = results['metrics']
            print(f"{proto:<20} {m['total_time']:<15} "
                  f"{m['avg_waiting_time']:<15.2f} "
                  f"{m['avg_turnaround_time']:<15.2f} "
                  f"{m['priority_inversion_duration']:<15}")

        if args.metrics_report:
            report = compare_protocols(
                [(r['metrics'], p) for r, _, p in results_list]
            )
            print(report)

        # Always generate comparison graphs in compare mode
        print(f"\n{'='*60}")
        print("Generating Comparison Graphs…")
        print(f"{'='*60}")
        plot_comparison_graphs(
            [(r['metrics'], p) for r, _, p in results_list],
            output_dir='output'
        )

        if args.visualize:
            print(f"\n{'='*60}")
            print("Generating Gantt Charts…")
            print(f"{'='*60}")
            visualize_all_protocols(
                [(r['timeline'], t, p) for r, t, p in results_list],
                output_dir='output'
            )

        if args.export_all:
            print(f"\n{'='*60}")
            print("Exporting Comparison Results…")
            print(f"{'='*60}")
            export_comparison(results_list, output_dir='output')

    # ── Single-protocol mode ──────────────────────────────────────────────────

    else:
        results, tasks = run_simulation(
            protocol, tasks, ceiling_priority,
            verbose=not args.realtime,
            realtime=args.realtime, delay=args.delay, interactive=args.interactive
        )

        if args.metrics_report:
            print_metrics_report(results['metrics'], protocol)

        if args.visualize:
            print(f"\nGenerating Gantt chart…")
            plot_gantt_chart(results['timeline'], tasks, protocol, output_dir='output')

        if args.export:
            export_results_to_csv(results, tasks, os.path.join('output', args.export))

        if args.export_json:
            export_to_json(results, tasks, os.path.join('output', args.export_json))

        if args.export_all:
            export_results(results, tasks, protocol, output_dir='output')

        if args.metrics_csv:
            export_metrics_to_csv(
                results['metrics'], tasks, protocol,
                os.path.join('output', args.metrics_csv)
            )


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_cli()
    else:
        main()
