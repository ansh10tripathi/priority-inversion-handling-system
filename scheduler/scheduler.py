"""Scheduler module for Priority Inversion Handling System."""

import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class Scheduler:
    """Preemptive priority scheduler."""

    def __init__(self):
        """Initialize the scheduler."""
        self.ready_queue = []
        self.current_time = 0

    def add_task(self, task):
        """
        Add a task to the ready queue.

        Args:
            task: Task to add
        """
        self.ready_queue.append(task)
        logger.info(f"Time {self.current_time}: Task {task.task_id} (Priority {task.priority}) added to ready queue")

    def get_next_task(self):
        """
        Select the highest priority ready task.

        Returns:
            Task with highest priority, or None if queue is empty
        """
        if not self.ready_queue:
            return None
        
        next_task = max(self.ready_queue, key=lambda t: t.priority)
        logger.info(f"Time {self.current_time}: Scheduled Task {next_task.task_id} (Priority {next_task.priority})")
        return next_task

    def remove_task(self, task):
        """
        Remove a task from the ready queue.

        Args:
            task: Task to remove
        """
        if task in self.ready_queue:
            self.ready_queue.remove(task)

    def check_arrivals(self, tasks):
        """
        Check for tasks arriving at current time.

        Args:
            tasks: List of all tasks to check
        """
        for task in tasks:
            if task.arrival_time == self.current_time and not task.completed:
                self.add_task(task)

    def step(self):
        """Advance time by one unit."""
        self.current_time += 1
