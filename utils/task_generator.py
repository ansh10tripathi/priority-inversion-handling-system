"""Task generator module for Priority Inversion Handling System."""

import random
from models import Task


class TaskGenerator:
    """Generates random tasks for simulation testing."""

    def __init__(self, number_of_tasks=5, max_priority=5, max_execution_time=10, 
                 max_arrival_time=5, resource_probability=0.5):
        """
        Initialize task generator with configuration.

        Args:
            number_of_tasks: Number of tasks to generate
            max_priority: Maximum priority value (1 to max_priority)
            max_execution_time: Maximum execution time for tasks
            max_arrival_time: Maximum arrival time for tasks
            resource_probability: Probability (0.0-1.0) that a task needs resource
        """
        self.number_of_tasks = number_of_tasks
        self.max_priority = max_priority
        self.max_execution_time = max_execution_time
        self.max_arrival_time = max_arrival_time
        self.resource_probability = resource_probability

    def generate(self):
        """
        Generate random tasks.

        Returns:
            List of Task objects
        """
        tasks = []
        for i in range(self.number_of_tasks):
            task = Task(
                task_id=f'T{i}',
                priority=random.randint(1, self.max_priority),
                arrival_time=random.randint(0, self.max_arrival_time),
                execution_time=random.randint(1, self.max_execution_time),
                needs_resource=random.random() < self.resource_probability
            )
            tasks.append(task)
        return tasks

    def generate_with_inversion_scenario(self):
        """
        Generate tasks designed to demonstrate priority inversion.

        Returns:
            List of Task objects with guaranteed priority inversion scenario
        """
        tasks = [
            # Low priority task that holds resource
            Task(
                task_id='Low',
                priority=1,
                arrival_time=0,
                execution_time=random.randint(3, self.max_execution_time),
                needs_resource=True
            ),
            # High priority task that needs resource
            Task(
                task_id='High',
                priority=self.max_priority,
                arrival_time=1,
                execution_time=random.randint(2, 5),
                needs_resource=True
            ),
            # Medium priority tasks that cause inversion
            Task(
                task_id='Med1',
                priority=self.max_priority // 2,
                arrival_time=2,
                execution_time=random.randint(2, 6),
                needs_resource=False
            )
        ]
        
        # Add additional random tasks
        for i in range(self.number_of_tasks - 3):
            task = Task(
                task_id=f'Extra{i}',
                priority=random.randint(1, self.max_priority),
                arrival_time=random.randint(3, self.max_arrival_time),
                execution_time=random.randint(1, self.max_execution_time),
                needs_resource=random.random() < self.resource_probability
            )
            tasks.append(task)
        
        return tasks


def generate_random_tasks(count=5, max_priority=5, max_execution_time=10, 
                         max_arrival_time=5, resource_probability=0.5):
    """
    Convenience function to generate random tasks.

    Args:
        count: Number of tasks to generate
        max_priority: Maximum priority value
        max_execution_time: Maximum execution time
        max_arrival_time: Maximum arrival time
        resource_probability: Probability that a task needs resource

    Returns:
        List of Task objects
    """
    generator = TaskGenerator(
        number_of_tasks=count,
        max_priority=max_priority,
        max_execution_time=max_execution_time,
        max_arrival_time=max_arrival_time,
        resource_probability=resource_probability
    )
    return generator.generate()


def generate_inversion_scenario(count=5, max_priority=5, max_execution_time=10):
    """
    Generate tasks with guaranteed priority inversion scenario.

    Args:
        count: Total number of tasks (minimum 3)
        max_priority: Maximum priority value
        max_execution_time: Maximum execution time

    Returns:
        List of Task objects
    """
    if count < 3:
        count = 3
    
    generator = TaskGenerator(
        number_of_tasks=count,
        max_priority=max_priority,
        max_execution_time=max_execution_time
    )
    return generator.generate_with_inversion_scenario()
