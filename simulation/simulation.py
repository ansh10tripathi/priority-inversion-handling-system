"""Simulation module for Priority Inversion Handling System."""

import logging
import time
from scheduler import Scheduler
from scheduler.protocols import detect_priority_inversion, apply_priority_inheritance, apply_priority_ceiling
from .metrics import MetricsCollector

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class Simulation:
    """Runs the scheduling simulation with priority inversion handling."""

    def __init__(self, tasks, mutex, protocol='None', realtime=False, delay=1.0, interactive=False):
        """
        Initialize simulation.

        Args:
            tasks: List of tasks to schedule
            mutex: Shared mutex resource
            protocol: Protocol to use ('None', 'PIP', 'PCP')
            realtime: Enable real-time step-by-step execution
            delay: Delay in seconds between time steps (for realtime mode)
            interactive: If True, wait for ENTER key instead of sleeping
        """
        self.tasks = tasks
        self.mutex = mutex
        self.protocol = protocol
        self.scheduler = Scheduler()
        self.timeline = []
        self.event_logs = []
        self.current_task = None
        self.metrics_collector = MetricsCollector()
        self.inversion_start_time = None
        self.inversion_high_task = None
        self.inversion_low_task = None
        self.task_states = {}  # Track task states for visualization
        self.realtime = realtime
        self.delay = delay
        self.interactive = interactive

    def run(self):
        """
        Run the simulation until all tasks complete.

        Returns:
            Dictionary containing timeline, logs, and metrics
        """
        logger.info(f"\n=== Starting Simulation with {self.protocol} Protocol ===\n")

        while not all(task.completed for task in self.tasks):
            self.step()
            self.scheduler.step()

        return self.get_results()

    def step(self):
        """Execute one time step of the simulation."""
        current_time = self.scheduler.current_time
        events = []

        if not self.realtime:
            logger.info(f"\n--- Time {current_time} ---")

        # Check for arriving tasks
        self.scheduler.check_arrivals(self.tasks)
        for task in self.tasks:
            if task.arrival_time == current_time:
                self.event_logs.append({"time": current_time, "type": "run",
                    "message": f"Task {task.task_id} arrived (priority={task.priority})"})

        # Handle mutex requests
        self.handle_mutex_requests()

        # Detect and track priority inversion
        inversion_detected = detect_priority_inversion(self.tasks, self.mutex)
        if inversion_detected:
            if self.inversion_start_time is None:
                self.inversion_start_time = current_time
                self.inversion_high_task = max(self.mutex.waiting_queue, key=lambda t: t.priority)
                self.inversion_low_task = self.mutex.owner
                self.event_logs.append({"time": current_time, "type": "inversion",
                    "message": f"Priority inversion detected: Task {self.inversion_high_task.task_id} "
                               f"blocked by Task {self.inversion_low_task.task_id}"})
        else:
            if self.inversion_start_time is not None:
                self.metrics_collector.record_priority_inversion(
                    self.inversion_start_time,
                    current_time,
                    self.inversion_high_task,
                    self.inversion_low_task
                )
                self.event_logs.append({"time": current_time, "type": "protocol",
                    "message": "Priority inversion resolved"})
                self.inversion_start_time = None
                self.inversion_high_task = None
                self.inversion_low_task = None

        # Apply protocols
        if self.protocol == 'PIP' and inversion_detected:
            apply_priority_inheritance(self.tasks, self.mutex)
            self.event_logs.append({"time": current_time, "type": "protocol",
                "message": f"PIP: Task {self.mutex.owner.task_id} priority raised to "
                           f"{self.mutex.owner.priority}"})

        # Select next task
        next_task = self.scheduler.get_next_task()

        # Record context switch
        if next_task != self.current_task:
            self.metrics_collector.record_context_switch(self.current_task, next_task)

        # Execute task
        if next_task:
            if next_task.start_time is None:
                next_task.start_time = current_time
            next_task.execute()
            self.current_task = next_task
            self.timeline.append((current_time, next_task.task_id))

            if next_task.completed:
                next_task.finish_time = current_time + 1
                self.event_logs.append({"time": current_time + 1, "type": "complete",
                    "message": f"Task {next_task.task_id} completed"})
                if next_task.has_resource:
                    self.restore_priority(next_task)
                    self.mutex.unlock()
                    self.unblock_waiting_tasks()
                elif self.protocol == 'PIP':
                    self.restore_priority(next_task)
                self.scheduler.remove_task(next_task)
                if not self.realtime:
                    logger.info(f"Task {next_task.task_id} completed")
        else:
            self.timeline.append((current_time, None))
            self.metrics_collector.record_idle()
            if not self.realtime:
                logger.info("CPU idle")

        # Display state after processing (realtime mode)
        if self.realtime:
            self._display_state(current_time, events)
            if self.interactive:
                input("Press ENTER for next step...")
            else:
                time.sleep(self.delay)

    def handle_mutex_requests(self):
        """Handle tasks requesting mutex access."""
        for task in self.scheduler.ready_queue:
            if task.needs_resource and not task.has_resource and not task.waiting:
                if self.mutex.lock(task):
                    if self.protocol == 'PCP':
                        old_p = task.priority
                        apply_priority_ceiling(task, self.mutex)
                        if task.priority != old_p:
                            self.event_logs.append({"time": self.scheduler.current_time, "type": "protocol",
                                "message": f"PCP: Task {task.task_id} priority raised "
                                           f"{old_p} → {task.priority}"})
                else:
                    self.mutex.add_to_waiting(task)
                    self.scheduler.remove_task(task)
                    self.event_logs.append({"time": self.scheduler.current_time, "type": "error",
                        "message": f"Task {task.task_id} blocked — waiting for mutex"})

    def restore_priority(self, task):
        """Restore task to original priority."""
        if task.priority != task.original_priority:
            logger.info(f"Task {task.task_id} priority restored to {task.original_priority}")
            task.priority = task.original_priority

    def unblock_waiting_tasks(self):
        """Move waiting tasks back to ready queue when mutex is released."""
        for task in list(self.mutex.waiting_queue):
            task.waiting = False
            self.scheduler.add_task(task)
        self.mutex.waiting_queue.clear()

    def _display_state(self, current_time, events=None):
        """Display formatted simulation state after each step."""
        print(f"\n{'─'*50}")
        print(f"Time {current_time}")
        print(f"{'─'*50}")

        # Running task
        if self.current_task and not self.current_task.completed:
            task = self.current_task
            priority_note = f" [priority raised: {task.original_priority}→{task.priority}]" \
                if task.priority != task.original_priority else ""
            mutex_note = " [holds mutex]" if task.has_resource else ""
            print(f"Running      : Task {task.task_id} (P={task.priority}){priority_note}{mutex_note}")
        else:
            print(f"Running      : IDLE")

        # Ready queue
        ready = sorted(self.scheduler.ready_queue, key=lambda t: t.priority, reverse=True)
        ready_str = ", ".join(f"{t.task_id}(P={t.priority})" for t in ready) if ready else "[]"
        print(f"Ready Queue  : [{ready_str}]" if ready else f"Ready Queue  : []")

        # Blocked tasks
        blocked = self.mutex.waiting_queue
        blocked_str = ", ".join(f"{t.task_id}(P={t.priority})" for t in blocked) if blocked else "None"
        print(f"Blocked      : {blocked_str}")

        # Mutex owner
        if self.mutex.owner:
            print(f"Mutex Owner  : Task {self.mutex.owner.task_id} (P={self.mutex.owner.priority})")
        else:
            print(f"Mutex Owner  : None")

        # Events
        for event in (events or []):
            print(f"Event        : {event}")
    
    def get_results(self):
        """
        Calculate and return simulation results.

        Returns:
            Dictionary with timeline, metrics, and logs
        """
        from .metrics import calculate_metrics
        
        metrics = calculate_metrics(
            self.tasks,
            self.scheduler.current_time,
            self.metrics_collector
        )

        if self.realtime:
            print(f"\n{'='*70}")
            print(f"[COMPLETE] Simulation Complete")
            print(f"{'='*70}")
            print(f"Total Time: {metrics['total_time']} time units")
            print(f"Average Waiting Time: {metrics['avg_waiting_time']:.2f} time units")
            print(f"Average Turnaround Time: {metrics['avg_turnaround_time']:.2f} time units")
            print(f"CPU Utilization: {metrics['cpu_utilization']:.2f}%")
            print(f"Priority Inversion Duration: {metrics['priority_inversion_duration']} time units")
        else:
            logger.info(f"\n=== Simulation Complete ===")
            logger.info(f"Total Time: {metrics['total_time']}")
            logger.info(f"Average Waiting Time: {metrics['avg_waiting_time']:.2f}")
            logger.info(f"Average Turnaround Time: {metrics['avg_turnaround_time']:.2f}")
            logger.info(f"CPU Utilization: {metrics['cpu_utilization']:.2f}%")

        return {
            'timeline': self.timeline,
            'metrics': metrics,
            'logs': self.event_logs,
            'protocol': self.protocol
        }
