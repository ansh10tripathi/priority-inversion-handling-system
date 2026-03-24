"""Priority inversion handling protocols."""

import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def detect_priority_inversion(tasks, mutex):
    """
    Detect if priority inversion is occurring.

    Priority inversion occurs when a high priority task is blocked waiting
    for a resource held by a lower priority task.

    Args:
        tasks: List of all tasks
        mutex: The mutex being checked

    Returns:
        True if priority inversion detected, False otherwise
    """
    if not mutex.locked or not mutex.waiting_queue:
        return False

    owner_priority = mutex.owner.priority
    for waiting_task in mutex.waiting_queue:
        if waiting_task.priority > owner_priority:
            logger.info(f"Priority inversion detected: Task {waiting_task.task_id} "
                       f"(Priority {waiting_task.priority}) blocked by Task {mutex.owner.task_id} "
                       f"(Priority {owner_priority})")
            return True
    return False


def apply_priority_inheritance(tasks, mutex):
    """
    Apply Priority Inheritance Protocol.

    Temporarily raises the priority of the resource owner to the highest
    priority of any task waiting for that resource.

    Args:
        tasks: List of all tasks
        mutex: The mutex to apply protocol to
    """
    if not mutex.locked or not mutex.waiting_queue:
        return

    max_waiting_priority = max(task.priority for task in mutex.waiting_queue)
    
    if max_waiting_priority > mutex.owner.priority:
        old_priority = mutex.owner.priority
        mutex.owner.priority = max_waiting_priority
        logger.info(f"Priority Inheritance: Task {mutex.owner.task_id} priority "
                   f"raised from {old_priority} to {max_waiting_priority}")


def apply_priority_ceiling(task, mutex):
    """
    Apply Priority Ceiling Protocol.

    When a task acquires a mutex, its priority is raised to the mutex's
    ceiling priority to prevent priority inversion.

    Args:
        task: Task acquiring the mutex
        mutex: The mutex being acquired

    Returns:
        True if protocol applied, False otherwise
    """
    if mutex.ceiling_priority is None:
        return False

    if task.has_resource and task.priority < mutex.ceiling_priority:
        old_priority = task.priority
        task.priority = mutex.ceiling_priority
        logger.info(f"Priority Ceiling: Task {task.task_id} priority "
                   f"raised from {old_priority} to {mutex.ceiling_priority}")
        return True
    return False
