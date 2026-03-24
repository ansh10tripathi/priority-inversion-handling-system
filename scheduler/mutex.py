"""Mutex module for Priority Inversion Handling System."""

import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class Mutex:
    """Simulates a shared resource with mutual exclusion."""

    def __init__(self, ceiling_priority=None):
        """
        Initialize a mutex.

        Args:
            ceiling_priority: Priority ceiling for priority ceiling protocol
        """
        self.locked = False
        self.owner = None
        self.waiting_queue = []
        self.ceiling_priority = ceiling_priority

    def lock(self, task):
        """
        Attempt to lock the mutex for a task.

        Args:
            task: Task requesting the lock

        Returns:
            True if lock acquired, False otherwise
        """
        if not self.locked:
            self.locked = True
            self.owner = task
            task.has_resource = True
            logger.info(f"Task {task.task_id} acquired mutex")
            return True
        logger.info(f"Task {task.task_id} blocked on mutex (owned by Task {self.owner.task_id})")
        return False

    def unlock(self):
        """Release the mutex."""
        if self.owner:
            logger.info(f"Task {self.owner.task_id} released mutex")
            self.owner.has_resource = False
            self.owner = None
        self.locked = False

    def add_to_waiting(self, task):
        """
        Add a task to the waiting queue.

        Args:
            task: Task to add to waiting queue
        """
        if task not in self.waiting_queue:
            self.waiting_queue.append(task)
            task.waiting = True
            logger.info(f"Task {task.task_id} added to mutex waiting queue")
