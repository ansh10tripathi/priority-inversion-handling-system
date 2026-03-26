"""Visualization module for Priority Inversion Handling System."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle


def plot_gantt_chart(timeline, tasks, protocol_name):
    """
    Create an enhanced Gantt chart visualization of the simulation.

    Args:
        timeline: List of (time, task_id) tuples
        tasks: List of Task objects
        protocol_name: Name of the protocol used
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Color scheme
    colors = {
        'running': '#3498db',      # Blue - task running
        'blocked': '#e74c3c',      # Red - task blocked
        'resource': '#f39c12',     # Orange - holding resource
        'priority_change': '#9b59b6'  # Purple - priority changed
    }
    
    # Build task execution data with states
    task_data = {task.task_id: [] for task in tasks}
    task_states = {task.task_id: [] for task in tasks}
    
    # Track task states through timeline
    for i, (time, task_id) in enumerate(timeline):
        if task_id:
            task = next(t for t in tasks if t.task_id == task_id)
            
            # Determine state
            has_resource = task.needs_resource and task.has_resource
            priority_changed = task.priority != task.original_priority
            
            if priority_changed:
                state = 'priority_change'
            elif has_resource:
                state = 'resource'
            else:
                state = 'running'
            
            task_data[task_id].append((time, 1, state))
    
    # Track blocked periods
    for task in tasks:
        if task.needs_resource:
            # Find periods when task was blocked
            blocked_start = None
            for time in range(task.arrival_time, task.finish_time if task.finish_time else len(timeline)):
                if time < len(timeline):
                    current_task = timeline[time][1]
                    if current_task != task.task_id and task.waiting:
                        if blocked_start is None:
                            blocked_start = time
                    else:
                        if blocked_start is not None:
                            task_data[task.task_id].append((blocked_start, time - blocked_start, 'blocked'))
                            blocked_start = None
    
    # Plot bars for each task
    y_pos = {task.task_id: i for i, task in enumerate(tasks)}
    
    for task in tasks:
        y = y_pos[task.task_id]
        
        # Group consecutive periods of same state
        if task.task_id in task_data:
            current_state = None
            start_time = None
            duration = 0
            
            for time, dur, state in sorted(task_data[task.task_id]):
                if state == current_state and time == start_time + duration:
                    # Continue current period
                    duration += dur
                else:
                    # Plot previous period
                    if current_state:
                        ax.barh(y, duration, left=start_time, height=0.6,
                               color=colors[current_state], edgecolor='black', linewidth=1.2)
                    # Start new period
                    current_state = state
                    start_time = time
                    duration = dur
            
            # Plot final period
            if current_state:
                ax.barh(y, duration, left=start_time, height=0.6,
                       color=colors[current_state], edgecolor='black', linewidth=1.2)
        
        # Add task labels with priority info
        if task.start_time is not None:
            label_text = f"{task.task_id}"
            if task.priority != task.original_priority:
                label_text += f" (P:{task.original_priority}→{task.priority})"
            ax.text(task.start_time - 0.5, y, label_text, 
                   ha='right', va='center', fontsize=9, fontweight='bold')
    
    # Configure chart
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([f"Task {t.task_id} (P={t.original_priority})" for t in tasks], fontsize=10)
    ax.set_xlabel('Time (units)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Tasks', fontsize=12, fontweight='bold')
    ax.set_title(f'Enhanced Gantt Chart - {protocol_name} Protocol\n'
                f'Execution Timeline with Resource Ownership and Priority Changes', 
                fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_xlim(0, len(timeline))
    
    # Enhanced legend
    legend_elements = [
        mpatches.Patch(color=colors['running'], label='Running (Normal)', edgecolor='black'),
        mpatches.Patch(color=colors['resource'], label='Running (Holding Resource)', edgecolor='black'),
        mpatches.Patch(color=colors['priority_change'], label='Running (Priority Changed)', edgecolor='black'),
        mpatches.Patch(color=colors['blocked'], label='Blocked (Waiting for Resource)', edgecolor='black')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10, framealpha=0.9)
    
    # Add protocol info box
    info_text = f"Protocol: {protocol_name}\n"
    info_text += f"Total Tasks: {len(tasks)}\n"
    info_text += f"Total Time: {len(timeline)} units"
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes,
           fontsize=9, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    filename = f'gantt_{protocol_name.lower()}.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Enhanced Gantt chart saved as: {filename}")
    plt.close()


def visualize_all_protocols(results_list):
    """
    Create Gantt charts for all protocol results.

    Args:
        results_list: List of (timeline, tasks, protocol_name) tuples
    """
    for timeline, tasks, protocol_name in results_list:
        plot_gantt_chart(timeline, tasks, protocol_name)
