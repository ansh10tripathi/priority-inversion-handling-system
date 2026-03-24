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

    def __init__(self, tasks, mutex, protocol='None', realtime=False, delay=1.0):
        """
        Initialize simulation.

        Args:
            tasks: List of tasks to schedule
            mutex: Shared mutex resource
            protocol: Protocol to use ('None', 'PIP', 'PCP')
            realtime: Enable real-time step-by-step execution
            delay: Delay in seconds between time steps (for realtime mode)
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
        
        if self.realtime:
            self._display_realtime_status(current_time)
        else:
            logger.info(f"\n--- Time {current_time} ---")

        # Check for arriving tasks
        self.scheduler.check_arrivals(self.tasks)

        # Handle mutex requests
        self.handle_mutex_requests()

        # Detect and track priority inversion
        inversion_detected = detect_priority_inversion(self.tasks, self.mutex)
        if inversion_detected:
            if self.inversion_start_time is None:
                # New inversion detected
                self.inversion_start_time = current_time
                self.inversion_high_task = max(self.mutex.waiting_queue, key=lambda t: t.priority)
                self.inversion_low_task = self.mutex.owner
                if self.realtime:
                    print(f"  [WARNING] PRIORITY INVERSION DETECTED!")
        else:
            if self.inversion_start_time is not None:
                # Inversion ended
                self.metrics_collector.record_priority_inversion(
                    self.inversion_start_time,
                    current_time,
                    self.inversion_high_task,
                    self.inversion_low_task
                )
                self.inversion_start_time = None
                self.inversion_high_task = None
                self.inversion_low_task = None

        # Apply protocols
        protocol_applied = False
        if self.protocol == 'PIP' and inversion_detected:
            apply_priority_inheritance(self.tasks, self.mutex)
            protocol_applied = True
            if self.realtime:
                print(f"  [PROTOCOL] Applying Priority Inheritance Protocol")
        elif self.protocol == 'PCP' and self.current_task:
            if apply_priority_ceiling(self.current_task, self.mutex):
                protocol_applied = True
                if self.realtime:
                    print(f"  [PROTOCOL] Applying Priority Ceiling Protocol")

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

            # Release mutex if task completed
            if next_task.completed:
                next_task.finish_time = current_time + 1
                if next_task.has_resource:
                    self.mutex.unlock()
                    self.restore_priority(next_task)
                    self.unblock_waiting_tasks()
                self.scheduler.remove_task(next_task)
                if not self.realtime:
                    logger.info(f"Task {next_task.task_id} completed")
        else:
            self.timeline.append((current_time, None))
            self.metrics_collector.record_idle()
            if not self.realtime:
                logger.info("CPU idle")
        
        # Sleep for realtime mode
        if self.realtime:
            time.sleep(self.delay)

    def handle_mutex_requests(self):
        """Handle tasks requesting mutex access."""
        for task in self.scheduler.ready_queue:
            if task.needs_resource and not task.has_resource and not task.waiting:
                if not self.mutex.lock(task):
                    self.mutex.add_to_waiting(task)
                    self.scheduler.remove_task(task)

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

    def _display_realtime_status(self, current_time):
        """Display real-time simulation status."""
        print(f"\n{'='*70}")
        print(f"[TIME {current_time}]")
        print(f"{'='*70}")
        
        # Running task
        if self.current_task:
            priority_str = f"P={self.current_task.priority}"
            if self.current_task.priority != self.current_task.original_priority:
                priority_str += f" (was {self.current_task.original_priority})"
            resource_str = " [HOLDS MUTEX]" if self.current_task.has_resource else ""
            print(f"Running: Task {self.current_task.task_id} ({priority_str}){resource_str}")
        else:
            print(f"CPU Idle")
        
        # Ready queue
        if self.scheduler.ready_queue:
            ready_tasks = sorted(self.scheduler.ready_queue, key=lambda t: t.priority, reverse=True)
            ready_str = ", ".join([f"{t.task_id}(P={t.priority})" for t in ready_tasks])
            print(f"Ready Queue: {ready_str}")
        else:
            print(f"Ready Queue: Empty")
        
        # Blocked tasks
        if self.mutex.waiting_queue:
            blocked_str = ", ".join([f"{t.task_id}(P={t.priority})" for t in self.mutex.waiting_queue])
            print(f"Blocked Tasks: {blocked_str}")
        else:
            print(f"Blocked Tasks: None")
        
        # Mutex owner
        if self.mutex.owner:
            print(f"Mutex Owner: Task {self.mutex.owner.task_id} (P={self.mutex.owner.priority})")
        else:
            print(f"Mutex: Available")
        
        # Task arrivals
        arriving = [t for t in self.tasks if t.arrival_time == current_time and not t.completed]
        if arriving:
            arrival_str = ", ".join([f"{t.task_id}(P={t.priority})" for t in arriving])
            print(f"Arriving: {arrival_str}")
    
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
            'protocol': self.protocol
        }
