"""
FastAPI backend for the Priority Inversion Handling System.

Run:
    pip install fastapi uvicorn
    uvicorn api:app --reload

Endpoints:
    GET  /run?protocol=None|PIP|PCP   — demo tasks
    POST /simulate                    — custom tasks
"""

import os
from typing import List, Literal, Optional
from fastapi import FastAPI, Query, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator, model_validator

from fastapi.middleware.cors import CORSMiddleware
from models import Task
from scheduler import Mutex
from simulation import Simulation

app = FastAPI(title="Priority Inversion Handling System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# Serve generated graph images as static files
os.makedirs("output", exist_ok=True)
app.mount("/output", StaticFiles(directory="output"), name="output")

# ── Step-mode session store ───────────────────────────────────────────────────
# Keyed by session_id (string). Each value is a live Simulation instance.
_sessions: dict = {}

# ── Pydantic schemas ──────────────────────────────────────────────────────────

VALID_PROTOCOLS = Literal["None", "PIP", "PCP"]


class TaskInput(BaseModel):
    name:           str   = Field(..., min_length=1, max_length=32)
    priority:       int   = Field(..., ge=1, le=100)
    arrival:        int   = Field(..., ge=0)
    execution:      int   = Field(..., ge=1)
    needs_resource: bool  = False


class SimulateRequest(BaseModel):
    protocol: VALID_PROTOCOLS = "None"
    tasks:    List[TaskInput] = Field(..., min_length=1, max_length=50)

    @field_validator("tasks")
    @classmethod
    def unique_names(cls, tasks: List[TaskInput]) -> List[TaskInput]:
        names = [t.name for t in tasks]
        if len(names) != len(set(names)):
            raise ValueError("Task names must be unique")
        return tasks

    @model_validator(mode="after")
    def resource_tasks_exist_for_pcp(self) -> "SimulateRequest":
        if self.protocol == "PCP":
            if not any(t.needs_resource for t in self.tasks):
                raise ValueError("PCP requires at least one task with needs_resource=true")
        return self


# ── Helpers ───────────────────────────────────────────────────────────────────

DEMO_TASKS_JSON = [
    {"name": "L",  "priority": 1, "arrival": 0, "execution": 10, "needs_resource": True},
    {"name": "H",  "priority": 5, "arrival": 4, "execution": 2,  "needs_resource": True},
    {"name": "M1", "priority": 3, "arrival": 1, "execution": 4,  "needs_resource": False},
    {"name": "M2", "priority": 4, "arrival": 2, "execution": 3,  "needs_resource": False},
]


def get_demo_tasks() -> List[Task]:
    return [
        Task(d["name"], priority=d["priority"], arrival_time=d["arrival"],
             execution_time=d["execution"], needs_resource=d["needs_resource"])
        for d in DEMO_TASKS_JSON
    ]


def _build_mutex(tasks: List[Task]) -> Mutex:
    """Ceiling = highest priority among resource-using tasks (or all tasks)."""
    resource_tasks = [t for t in tasks if t.needs_resource]
    ceiling = max((t.priority for t in resource_tasks), default=max(t.priority for t in tasks))
    return Mutex(ceiling_priority=ceiling)


def _run_sim(tasks: List[Task], protocol: str) -> dict:
    mutex = _build_mutex(tasks)
    try:
        results = Simulation(tasks, mutex, protocol=protocol).run()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "timeline": [{"time": t, "task": tid} for t, tid in results["timeline"]],
        "metrics":  results["metrics"],
        "logs":     results["logs"],
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/default-tasks")
def default_tasks():
    """Return the canonical demo task set as JSON."""
    return DEMO_TASKS_JSON


@app.get("/run")
def run_demo(protocol: str = Query("None", pattern="^(None|PIP|PCP)$")):
    """Run simulation with built-in demo tasks (L, H, M1, M2)."""
    return _run_sim(get_demo_tasks(), protocol)


@app.post("/simulate")
def simulate(body: SimulateRequest):
    """Run simulation with caller-supplied tasks and protocol."""
    tasks = [
        Task(
            task_id=t.name,
            priority=t.priority,
            arrival_time=t.arrival,
            execution_time=t.execution,
            needs_resource=t.needs_resource,
        )
        for t in body.tasks
    ]
    return _run_sim(tasks, body.protocol)


class GenerateGraphsRequest(BaseModel):
    tasks: List[TaskInput] = Field(default=[])


@app.post("/generate-graphs")
def generate_graphs(body: GenerateGraphsRequest = GenerateGraphsRequest()):
    """Run all 3 protocols on the given tasks and save Gantt + comparison graphs."""
    from visualization.gantt_chart import plot_gantt_chart
    from visualization.performance_graphs import plot_comparison_graphs
    import copy

    raw_tasks = body.tasks if body.tasks else [
        TaskInput(**{"name": d["name"], "priority": d["priority"], "arrival": d["arrival"],
                     "execution": d["execution"], "needs_resource": d["needs_resource"]})
        for d in DEMO_TASKS_JSON
    ]

    comparison_data = []
    for protocol in ("None", "PIP", "PCP"):
        tasks = [
            Task(task_id=t.name, priority=t.priority, arrival_time=t.arrival,
                 execution_time=t.execution, needs_resource=t.needs_resource)
            for t in raw_tasks
        ]
        mutex  = _build_mutex(tasks)
        sim    = Simulation(tasks, mutex, protocol=protocol)
        result = sim.run()
        try:
            plot_gantt_chart(result["timeline"], tasks, protocol, output_dir="output")
        except Exception:
            pass
        comparison_data.append((result["metrics"], protocol))

    try:
        plot_comparison_graphs(comparison_data, output_dir="output")
    except Exception:
        pass

    return {"ok": True}


# ── Step-mode endpoints ───────────────────────────────────────────────────────

class StepInitRequest(BaseModel):
    tasks: List[TaskInput] = Field(default=[])


@app.post("/step/init")
def step_init(body: StepInitRequest = StepInitRequest(),
             protocol: str = Query("None", pattern="^(None|PIP|PCP)$"),
             session_id: str = Query("default")):
    """Create a new step-mode session. Uses supplied tasks or falls back to demo."""
    if body.tasks:
        tasks = [
            Task(task_id=t.name, priority=t.priority, arrival_time=t.arrival,
                 execution_time=t.execution, needs_resource=t.needs_resource)
            for t in body.tasks
        ]
    else:
        tasks = get_demo_tasks()
    mutex = _build_mutex(tasks)
    sim   = Simulation(tasks, mutex, protocol=protocol)
    _sessions[session_id] = sim
    return {"session_id": session_id, "protocol": protocol, "done": False}


@app.post("/step/next")
def step_next(session_id: str = Query("default")):
    """Advance the simulation by one time unit and return the new state."""
    sim = _sessions.get(session_id)
    if sim is None:
        raise HTTPException(status_code=404, detail="Session not found. Call /step/init first.")

    done = all(t.completed for t in sim.tasks)
    if done:
        return _step_snapshot(sim, done=True)

    # Capture log length before the step so we can return only new entries
    prev_log_len = len(sim.event_logs)

    sim.step()
    sim.scheduler.step()

    done = all(t.completed for t in sim.tasks)
    new_logs = sim.event_logs[prev_log_len:]

    # Latest timeline entry
    last = sim.timeline[-1] if sim.timeline else None
    tick = {"time": last[0], "task": last[1]} if last else None

    # If the step just finished the simulation, return the full terminal snapshot
    if done:
        snap = _step_snapshot(sim, done=True)
        snap["tick"]     = tick
        snap["new_logs"] = new_logs
        return snap

    # Current scheduler state
    ready   = [{"id": t.task_id, "priority": t.priority} for t in sim.scheduler.ready_queue]
    blocked = [{"id": t.task_id, "priority": t.priority} for t in sim.mutex.waiting_queue]
    mutex_owner = sim.mutex.owner.task_id if sim.mutex.owner else None

    return {
        "done":         False,
        "tick":         tick,
        "new_logs":     new_logs,
        "ready":        ready,
        "blocked":      blocked,
        "mutex_owner":  mutex_owner,
        "current_time": sim.scheduler.current_time,
    }


@app.delete("/step/reset")
def step_reset(session_id: str = Query("default")):
    """Destroy a step-mode session."""
    _sessions.pop(session_id, None)
    return {"ok": True}


def _step_snapshot(sim: Simulation, done: bool) -> dict:
    """Return a terminal snapshot when the simulation is already finished."""
    from simulation.metrics import calculate_metrics
    metrics = calculate_metrics(sim.tasks, sim.scheduler.current_time, sim.metrics_collector)
    return {
        "done":        True,
        "tick":        None,
        "new_logs":    [],
        "ready":       [],
        "blocked":     [],
        "mutex_owner": None,
        "current_time": sim.scheduler.current_time,
        "metrics":     metrics,
        "timeline":    [{"time": t, "task": tid} for t, tid in sim.timeline],
        "logs":        sim.event_logs,
    }
