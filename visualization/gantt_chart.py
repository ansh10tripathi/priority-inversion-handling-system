"""Gantt chart visualization module for Priority Inversion Handling System."""

import warnings
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import os


def plot_gantt_chart(timeline, tasks, protocol_name, output_dir='output',
                     rich_timeline=None):
    """
    Create an enhanced Gantt chart visualization of the simulation.

    Args:
        timeline: List of (time, task_id) tuples
        tasks: List of Task objects
        protocol_name: Name of the protocol used
        output_dir: Directory to save the chart (default: 'output')
        rich_timeline: Optional list of (time, task_id, state) tuples where
                       state is 'running' | 'resource' | 'priority_change'.
                       When provided, used instead of inferring state from
                       post-simulation task attributes.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    fig, ax = plt.subplots(figsize=(14, 8))

    colors = {
        'running':         '#3498db',   # blue
        'blocked':         '#e74c3c',   # red
        'resource':        '#f39c12',   # orange
        'priority_change': '#9b59b6',   # purple
    }

    # ── Build per-task bar data ──────────────────────────────────────────────
    # task_bars[task_id] = list of (start_time, state)
    task_bars = {task.task_id: [] for task in tasks}

    if rich_timeline:
        # Use pre-captured states — accurate regardless of post-sim attribute values
        for time, task_id, state in rich_timeline:
            if task_id:
                task_bars[task_id].append((time, state))
    else:
        # Fallback: infer from post-simulation task attributes (less accurate)
        for time, task_id in timeline:
            if task_id:
                task = next(t for t in tasks if t.task_id == task_id)
                if task.priority != task.original_priority:
                    state = 'priority_change'
                elif task.needs_resource:
                    state = 'resource'
                else:
                    state = 'running'
                task_bars[task_id].append((time, state))

    # ── Track blocked periods from timeline gaps ─────────────────────────────
    running_set = {time for time, tid in timeline if tid}
    for task in tasks:
        if not task.needs_resource or task.finish_time is None:
            continue
        for time in range(task.arrival_time, task.finish_time):
            if time not in running_set:
                # Check if any other task was running (not idle)
                slot_task = next((tid for t, tid in timeline if t == time and tid), None)
                if slot_task and slot_task != task.task_id:
                    task_bars[task.task_id].append((time, 'blocked'))

    # ── Plot bars ────────────────────────────────────────────────────────────
    y_pos = {task.task_id: i for i, task in enumerate(tasks)}

    for task in tasks:
        y    = y_pos[task.task_id]
        bars = sorted(task_bars[task.task_id], key=lambda x: x[0])

        # Merge consecutive same-state slots into single bars
        merged = []
        for time, state in bars:
            if merged and merged[-1][2] == state and merged[-1][0] + merged[-1][1] == time:
                merged[-1] = (merged[-1][0], merged[-1][1] + 1, state)
            else:
                merged.append((time, 1, state))

        for start, duration, state in merged:
            ax.barh(y, duration, left=start, height=0.6,
                    color=colors[state], edgecolor='black', linewidth=1.2)

        # Task label
        if task.start_time is not None:
            label = task.task_id
            if task.priority != task.original_priority:
                label += f' (P:{task.original_priority}->{task.priority})'
            ax.text(task.start_time - 0.3, y, label,
                    ha='right', va='center', fontsize=9, fontweight='bold')

    # ── Axes ─────────────────────────────────────────────────────────────────
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels(
        [f'Task {t.task_id} (P={t.original_priority})' for t in tasks],
        fontsize=10)
    ax.set_xlabel('Time (units)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tasks', fontsize=12, fontweight='bold')
    ax.set_title(
        f'Enhanced Gantt Chart - {protocol_name} Protocol\n'
        f'Execution Timeline with Resource Ownership and Priority Changes',
        fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_xlim(0, len(timeline))

    # ── Legend (fix: use facecolor not color to avoid UserWarning) ────────────
    legend_elements = [
        mpatches.Patch(facecolor=colors['running'],         edgecolor='black',
                       label='Running (Normal)'),
        mpatches.Patch(facecolor=colors['resource'],        edgecolor='black',
                       label='Running (Holding Resource)'),
        mpatches.Patch(facecolor=colors['priority_change'], edgecolor='black',
                       label='Running (Priority Changed)'),
        mpatches.Patch(facecolor=colors['blocked'],         edgecolor='black',
                       label='Blocked (Waiting for Resource)'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10, framealpha=0.9)

    # ── Info box ─────────────────────────────────────────────────────────────
    info_text = (f'Protocol: {protocol_name}\n'
                 f'Total Tasks: {len(tasks)}\n'
                 f'Total Time: {len(timeline)} units')
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
            fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()
    filename = os.path.join(output_dir, f'gantt_{protocol_name.lower()}.png')
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f'Enhanced Gantt chart saved as: {filename}')
    plt.close()


def visualize_all_protocols(results_list, output_dir='output'):
    """
    Create Gantt charts for all protocol results.

    Args:
        results_list: List of (timeline, tasks, protocol_name) tuples
        output_dir: Directory to save charts (default: 'output')
    """
    for timeline, tasks, protocol_name in results_list:
        plot_gantt_chart(timeline, tasks, protocol_name, output_dir)
