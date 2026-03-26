"""Controller: bridges the GUI with the existing simulation backend."""

import copy
import sys
import os

# Allow imports from project root when running gui.py directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models import Task
from scheduler import Scheduler, Mutex
from scheduler.protocols import (
    detect_priority_inversion,
    apply_priority_inheritance,
    apply_priority_ceiling,
)
from simulation.metrics import MetricsCollector, calculate_metrics


# ── Default scenario (the classic priority-inversion demo) ──────────────────

DEFAULT_TASKS = [
    dict(task_id='L', priority=1, arrival_time=0, execution_time=3, needs_resource=True),
    dict(task_id='H', priority=3, arrival_time=1, execution_time=2, needs_resource=True),
    dict(task_id='M', priority=2, arrival_time=2, execution_time=3, needs_resource=False),
]


def _make_tasks(task_dicts):
    return [Task(**d) for d in task_dicts]


# ── Step snapshot ────────────────────────────────────────────────────────────

class StepSnapshot:
    """Everything the GUI needs to know after one simulation step."""

    __slots__ = (
        'time', 'running', 'ready', 'blocked',
        'mutex_owner', 'events', 'done', 'metrics',
    )

    def __init__(self, time, running, ready, blocked,
                 mutex_owner, events, done, metrics=None):
        self.time        = time
        self.running     = running      # task_id str or None
        self.ready       = ready        # list of (task_id, priority)
        self.blocked     = blocked      # list of (task_id, priority)
        self.mutex_owner = mutex_owner  # task_id str or None
        self.events      = events       # list of str
        self.done        = done         # bool – all tasks completed
        self.metrics     = metrics      # dict, populated only when done=True


# ── SimController ────────────────────────────────────────────────────────────

class SimController:
    """
    Drives the simulation one step at a time.

    The GUI calls:
        reset(task_dicts, protocol)   – initialise / re-initialise
        tick()                        – advance one time unit → StepSnapshot
    """

    def __init__(self):
        self._task_dicts     = None
        self._protocol       = 'None'
        self._tasks          = []
        self._mutex          = None
        self._scheduler      = None
        self._metrics        = None
        self._current_task   = None
        self._inv_start      = None
        self._inv_high       = None
        self._inv_low        = None
        self._finished       = False

    # ── public ──────────────────────────────────────────────────────────────

    def reset(self, task_dicts, protocol):
        """(Re-)initialise with a fresh set of tasks and chosen protocol."""
        self._task_dicts   = task_dicts
        self._protocol     = protocol
        ceiling            = max(d['priority'] for d in task_dicts) if protocol == 'PCP' else None
        self._tasks        = _make_tasks(task_dicts)
        self._mutex        = Mutex(ceiling_priority=ceiling)
        self._scheduler    = Scheduler()
        self._metrics      = MetricsCollector()
        self._current_task = None
        self._inv_start    = None
        self._inv_high     = None
        self._inv_low      = None
        self._finished     = False
        self._timeline      = []
        self._rich_timeline = []
        # Silence only the noisy backend loggers (scheduler internals)
        # so they don't pollute the terminal with raw log lines.
        # We replace them with clean per-step prints in tick().
        import logging
        for name in ('scheduler', 'scheduler.scheduler',
                     'scheduler.mutex', 'scheduler.protocols', 'simulation'):
            logging.getLogger(name).setLevel(logging.CRITICAL)

    def is_finished(self):
        return self._finished

    def tick(self):
        """Execute one time unit and return a StepSnapshot."""
        # Guard: return a stable done snapshot if already finished
        if self._finished:
            return self._done_snapshot(self._scheduler.current_time)

        t      = self._scheduler.current_time
        events = []

        # 1. Arrivals
        self._scheduler.check_arrivals(self._tasks)

        # 2. Mutex requests
        self._handle_mutex_requests()

        # 3. Inversion detection
        inv = detect_priority_inversion(self._tasks, self._mutex)
        if inv:
            if self._inv_start is None:
                self._inv_start = t
                self._inv_high  = max(self._mutex.waiting_queue, key=lambda x: x.priority)
                self._inv_low   = self._mutex.owner
                events.append('[!] Priority Inversion Detected')
                high = self._inv_high
                low  = self._inv_low
                events.append(
                    f'    Task {high.task_id}(P={high.priority}) blocked by '
                    f'Task {low.task_id}(P={low.original_priority})')
        else:
            if self._inv_start is not None:
                self._metrics.record_priority_inversion(
                    self._inv_start, t, self._inv_high, self._inv_low)
                self._inv_start = None
                self._inv_high  = None
                self._inv_low   = None

        # 4. Protocol application
        if self._protocol == 'PIP' and inv:
            apply_priority_inheritance(self._tasks, self._mutex)
            owner = self._mutex.owner
            events.append(
                f'[P] PIP: Task {owner.task_id} priority raised to {owner.priority}')
        elif self._protocol == 'PCP' and self._current_task:
            if apply_priority_ceiling(self._current_task, self._mutex):
                ct = self._current_task
                events.append(
                    f'[P] PCP: Task {ct.task_id} raised to ceiling {ct.priority}')

        # 5. Schedule next task
        next_task = self._scheduler.get_next_task()
        if next_task != self._current_task:
            self._metrics.record_context_switch(self._current_task, next_task)

        # 6. Execute
        if next_task:
            if next_task.start_time is None:
                next_task.start_time = t
            # Capture state BEFORE execute() so has_resource/priority are current
            if next_task.priority != next_task.original_priority:
                state = 'priority_change'
            elif next_task.has_resource:
                state = 'resource'
            else:
                state = 'running'
            next_task.execute()
            self._current_task = next_task
            self._timeline.append((t, next_task.task_id))
            self._rich_timeline.append((t, next_task.task_id, state))

            if next_task.completed:
                next_task.finish_time = t + 1
                events.append(f'[+] Task {next_task.task_id} Completed')
                if next_task.has_resource:
                    events.append(f'    Mutex released by Task {next_task.task_id}')
                    self._mutex.unlock()
                    self._restore_priority(next_task)
                    self._unblock_waiting()
                self._scheduler.remove_task(next_task)
        else:
            self._metrics.record_idle()

        # 7. Advance clock
        self._scheduler.step()

        # 8. Print clean step summary to terminal
        running_id = next_task.task_id if next_task else None
        blocked_ids = [t2.task_id for t2 in self._mutex.waiting_queue]
        ready_ids   = [t2.task_id for t2 in self._scheduler.ready_queue
                       if t2.task_id != running_id]
        owner_id    = self._mutex.owner.task_id if self._mutex.owner else 'None'

        print(f"\n{'-'*48}")
        print(f" Time        : {t}")
        print(f" Protocol    : {self._protocol}")
        print(f" Running     : {running_id if running_id else 'IDLE'}")
        print(f" Ready Queue : {ready_ids if ready_ids else '[]'}")
        print(f" Blocked     : {blocked_ids if blocked_ids else '[]'}")
        print(f" Mutex Owner : {owner_id}")
        for ev in events:
            print(f" Event       : {ev}")

        # 9. Check completion
        if all(task.completed for task in self._tasks):
            self._finished = True
            snap = self._done_snapshot(t, next_task, events)
            m = snap.metrics
            print(f"\n{'='*48}")
            print(f" SIMULATION COMPLETE")
            print(f" Total Time      : {m['total_time']}")
            print(f" Avg Wait        : {m['avg_waiting_time']:.2f}")
            print(f" Avg Turnaround  : {m['avg_turnaround_time']:.2f}")
            print(f" CPU Utilization : {m['cpu_utilization']:.1f}%")
            print(f" Inv. Count      : {m['priority_inversion_count']}")
            print(f" Inv. Duration   : {m['priority_inversion_duration']}")
            print(f"{'='*48}")
            return snap

        # 9. Build snapshot — exclude running task from ready queue display
        running_id  = next_task.task_id if next_task else None
        ready_list  = [
            (t2.task_id, t2.priority)
            for t2 in self._scheduler.ready_queue
            if t2.task_id != running_id
        ]
        return StepSnapshot(
            time        = t,
            running     = running_id,
            ready       = ready_list,
            blocked     = [(t2.task_id, t2.priority) for t2 in self._mutex.waiting_queue],
            mutex_owner = self._mutex.owner.task_id if self._mutex.owner else None,
            events      = events,
            done        = False,
        )

    # ── private ─────────────────────────────────────────────────────────────

    def _handle_mutex_requests(self):
        for task in list(self._scheduler.ready_queue):
            if task.needs_resource and not task.has_resource and not task.waiting:
                if not self._mutex.lock(task):
                    self._mutex.add_to_waiting(task)
                    self._scheduler.remove_task(task)

    def _restore_priority(self, task):
        if task.priority != task.original_priority:
            task.priority = task.original_priority

    def _unblock_waiting(self):
        for task in list(self._mutex.waiting_queue):
            task.waiting = False
            self._scheduler.add_task(task)
        self._mutex.waiting_queue.clear()

    def _done_snapshot(self, last_time=0, last_task=None, events=None):
        metrics = calculate_metrics(
            self._tasks, self._scheduler.current_time, self._metrics)
        return StepSnapshot(
            time        = last_time,
            running     = last_task.task_id if (last_task and not last_task.completed) else None,
            ready       = [],
            blocked     = [],
            mutex_owner = None,
            events      = (events or []) + ['[+] Simulation Complete'],
            done        = True,
            metrics     = metrics,
        )
