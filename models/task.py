"""Task module for Priority Inversion Handling System."""


class Task:
    """Represents a task in the scheduling system."""

    def __init__(self, task_id, priority, arrival_time, execution_time, needs_resource=False):
        """
        Initialize a task.

        Args:
            task_id: Unique identifier for the task
            priority: Task priority (higher value = higher priority)
            arrival_time: Time when task arrives in the system
            execution_time: Total time required to complete the task
            needs_resource: Whether task requires a shared resource
        """
        self.task_id = task_id
        self.priority = priority
        self.original_priority = priority
        self.arrival_time = arrival_time
        self.execution_time = execution_time
        self.remaining_time = execution_time
        self.needs_resource = needs_resource
        self.has_resource = False
        self.waiting = False
        self.completed = False
        self.start_time = None
        self.finish_time = None

    def execute(self):
        """Execute the task for one time unit."""
        if self.start_time is None:
            self.start_time = 0
        self.remaining_time -= 1
        if self.remaining_time == 0:
            self.completed = True

    def get_waiting_time(self, current_time):
        """
        Calculate waiting time.

        Args:
            current_time: Current system time

        Returns:
            Total waiting time (turnaround time - execution time)
        """
        if self.finish_time is None:
            return 0
        return self.finish_time - self.arrival_time - self.execution_time

    def get_turnaround_time(self):
        """
        Calculate turnaround time.

        Returns:
            Total time from arrival to completion
        """
        if self.finish_time is None:
            return 0
        return self.finish_time - self.arrival_time
