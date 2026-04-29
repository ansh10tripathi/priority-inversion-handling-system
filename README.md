# Priority Inversion Handling System

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

A full-stack web-based educational simulator for demonstrating and analysing **priority inversion** in real-time operating systems. Implements three scheduling protocols — None (baseline), PIP, and PCP — with an interactive React dashboard, animated Gantt charts, step-by-step execution mode, and comprehensive performance metrics.

---

## Table of Contents

- [Overview](#overview)
- [What is Priority Inversion?](#what-is-priority-inversion)
- [Protocols Implemented](#protocols-implemented)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [Frontend Pages](#frontend-pages)
- [Features](#features)
- [Example Output](#example-output)
- [CLI Usage](#cli-usage)
- [Future Improvements](#future-improvements)
- [References](#references)
- [License](#license)

---

## Overview

This project simulates priority inversion scenarios in real-time operating systems and demonstrates how different protocols handle this critical scheduling anomaly.

**Key Highlights:**
- Full-stack web application (FastAPI backend + React 19 frontend)
- Interactive Gantt chart with tick-by-tick animation
- Step-by-step execution mode with live scheduler state
- Auto-play mode with adjustable speed slider
- Task CRUD editor — define custom task sets or use the built-in demo
- Protocol comparison table with best-value highlighting
- Filterable event log viewer
- PNG graph export (Gantt + comparison charts)
- Legacy CLI interface still available

---

## What is Priority Inversion?

**Priority inversion** is a scheduling anomaly where a high-priority task is indirectly blocked by a lower-priority task, violating the priority-based scheduling principle.

```
Time 0: Low priority task (L) acquires mutex
Time 1: High priority task (H) needs mutex → BLOCKED
Time 2: Medium priority task (M) preempts L
Result: H waits for both M and L  ← INVERSION
```

**Real-world impact — Mars Pathfinder (1997):** NASA's Mars Pathfinder experienced system resets due to priority inversion. The issue was resolved by enabling Priority Inheritance Protocol in the VxWorks RTOS.

---

## Protocols Implemented

### None (Baseline)
Standard preemptive priority scheduling with no inversion handling. Used as a reference for comparison.

### Priority Inheritance Protocol (PIP)
**Reactive:** When a high-priority task blocks on a resource, the mutex owner temporarily inherits the higher priority.

- Simple to implement, transparent to tasks
- Reactive — inversion must occur before it is corrected
- Potential for deadlock with multiple resources

### Priority Ceiling Protocol (PCP)
**Proactive:** Each mutex has a ceiling priority equal to the highest priority of any task that uses it. When a task acquires the mutex its priority is immediately raised to the ceiling.

- Prevents inversion before it occurs
- More predictable, prevents deadlock with proper ceiling assignment
- Requires prior knowledge of all tasks using the resource

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                Priority Inversion System                 │
│                                                          │
│  React Frontend (port 3000)                              │
│  ├── Dashboard   — KPIs, protocol info, compare table    │
│  ├── Simulation  — Gantt animation, step/auto-play mode  │
│  ├── Metrics     — Charts, full metrics table, PNG graphs│
│  ├── Logs        — Filterable event log                  │
│  └── Tasks       — Task CRUD editor                      │
│                          │ HTTP / Axios                  │
│  FastAPI Backend (port 8000)                             │
│  ├── api.py      — All endpoints, step-mode sessions     │
│  ├── models/     — Task class                            │
│  ├── scheduler/  — Scheduler, Mutex, PIP/PCP protocols   │
│  ├── simulation/ — Simulation orchestrator, metrics      │
│  ├── utils/      — Task generator, CSV/JSON exporter     │
│  └── visualization/ — Gantt + comparison PNG generation  │
└──────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
priority_inversion_system/
│
├── api.py                       ← FastAPI app — all HTTP endpoints
├── main.py                      ← Legacy CLI entry point
├── requirements.txt
├── tasks_config.json            ← Sample task config
├── complex_tasks.json           ← Larger sample task config
├── visualization.py             ← Legacy standalone visualiser
│
├── models/
│   └── task.py                  ← Task class
│
├── scheduler/
│   ├── scheduler.py             ← Preemptive priority scheduler
│   ├── mutex.py                 ← Mutex resource management
│   └── protocols.py             ← detect_priority_inversion, apply_pip, apply_pcp
│
├── simulation/
│   ├── simulation.py            ← Simulation orchestrator + step() method
│   └── metrics.py               ← MetricsCollector, calculate_metrics
│
├── utils/
│   ├── task_generator.py        ← Random task generation
│   └── exporter.py              ← CSV / JSON export
│
├── visualization/
│   ├── gantt_chart.py           ← plot_gantt_chart() — saves PNG to output/
│   └── performance_graphs.py    ← plot_comparison_graphs() — saves PNGs to output/
│
├── output/                      ← Generated PNG / CSV / JSON artefacts
│   ├── gantt_none.png
│   ├── gantt_pip.png
│   ├── gantt_pcp.png
│   ├── comparison_waiting_time.png
│   ├── comparison_turnaround_time.png
│   ├── comparison_context_switches.png
│   └── comparison_inversion_duration.png
│
└── frontend/
    ├── package.json
    ├── tailwind.config.js
    ├── postcss.config.js
    └── src/
        ├── App.js               ← Root component, global state, sidebar, topbar
        ├── index.css            ← CSS variables + utility classes
        ├── GanttChart.js        ← Interactive tick-grid Gantt component
        ├── MetricsPanel.js      ← Bar charts + stat cards (Chart.js)
        ├── EventLog.js          ← Scrollable log list (step mode)
        ├── components/
        │   └── ProtocolTabs.js  ← Reusable 3-tab protocol switcher
        └── pages/
            ├── DashboardPage.js ← KPI cards, protocol info, activity feed, compare table
            ├── SimulationPage.js← Controls, speed slider, Gantt animation, step mode
            ├── MetricsPage.js   ← Explainer cards, full metrics table, PNG graphs
            ├── LogsPage.js      ← Filterable event log table
            └── TasksPage.js     ← Task CRUD editor
```

---

## Installation

### Prerequisites

- Python 3.13+
- Node.js 18+ and npm

### Backend

```bash
cd priority_inversion_system
pip install fastapi uvicorn matplotlib
```

Or with a requirements file:

```bash
pip install -r requirements.txt
pip install fastapi uvicorn   # add these if not already in requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

---

## Running the Application

### Start the backend

```bash
# From project root
uvicorn api:app --reload
# Runs at http://127.0.0.1:8000
```

### Start the frontend

```bash
cd frontend
npm start
# Runs at http://localhost:3000
```

Open `http://localhost:3000` in your browser.

---

## API Reference

Base URL: `http://127.0.0.1:8000`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/default-tasks` | Returns the 4 built-in demo tasks |
| GET | `/run?protocol=None\|PIP\|PCP` | Runs demo tasks with the given protocol |
| POST | `/simulate` | Runs custom tasks — see request body below |
| POST | `/generate-graphs` | Runs all 3 protocols and saves PNGs to `output/` |
| POST | `/step/init?protocol=&session_id=` | Creates a step-mode session |
| POST | `/step/next?session_id=` | Advances the session by one tick |
| DELETE | `/step/reset?session_id=` | Destroys a session |

Static files in `output/` are served at `/output/<filename>`.

### POST `/simulate` — request body

```json
{
  "protocol": "PIP",
  "tasks": [
    { "name": "L",  "priority": 1, "arrival": 0, "execution": 10, "needs_resource": true  },
    { "name": "H",  "priority": 5, "arrival": 4, "execution": 2,  "needs_resource": true  },
    { "name": "M1", "priority": 3, "arrival": 1, "execution": 4,  "needs_resource": false },
    { "name": "M2", "priority": 4, "arrival": 2, "execution": 3,  "needs_resource": false }
  ]
}
```

Constraints: 1–50 tasks, unique names, priority 1–100, execution ≥ 1. PCP requires at least one task with `needs_resource: true`.

### Response shape

```json
{
  "timeline": [{ "time": 0, "task": "L" }, ...],
  "metrics":  { "total_time": 14, "avg_waiting_time": 1.67, ... },
  "logs":     [{ "time": 0, "type": "run", "message": "Task L arrived" }, ...]
}
```

### Metrics fields

| Field | Description |
|-------|-------------|
| `total_time` | Total simulation duration (time units) |
| `avg_waiting_time` | Average time tasks spent waiting |
| `avg_turnaround_time` | Average time from arrival to completion |
| `avg_response_time` | Average time from arrival to first execution |
| `cpu_utilization` | Percentage of time CPU was busy |
| `context_switches` | Number of task switches |
| `priority_inversion_count` | Number of inversion events detected |
| `priority_inversion_duration` | Total time units spent in inversion |
| `throughput` | Tasks completed per time unit |

### Log event types

`run` | `inversion` | `protocol` | `complete` | `error` | `idle`

---

## Frontend Pages

### Dashboard
- KPI cards: Total Time, Avg Waiting Time, CPU Utilization, Inversion Count
- Active Protocol info card with secondary metrics
- Recent Activity feed (notable events only)
- Protocol Comparison table with best-value highlighting (toggle with "Compare All")

### Simulation
- Protocol selector and Full Run / Step mode toggle
- Speed slider for auto-play (100 ms – 2000 ms per tick)
- Interactive Gantt chart with colour-coded states:
  - Blue — running (normal)
  - Orange — running while holding resource
  - Purple — running with raised priority
  - Red — blocked waiting for resource
- Live scheduler state panel (ready queue, blocked queue, mutex owner)
- Step-by-step event log

### Metrics
- Explainer cards for each protocol
- Full metrics table for all completed protocols
- Embedded PNG comparison graphs (generated server-side by matplotlib)

### Logs
- Filterable event log table by event type and protocol
- Colour-coded rows matching event severity

### Tasks
- Add, edit, and delete tasks
- Toggle `needs_resource` flag
- Load built-in demo task set
- Task count badge in sidebar when custom tasks are active

---

## Features

- Preemptive priority scheduling — always runs the highest-priority ready task
- Priority inversion detection — automatically detects and tracks inversion events
- Three protocol implementations — None, PIP, PCP
- Step-by-step execution — advance one tick at a time with live scheduler state
- Auto-play mode — continuous playback with adjustable speed
- Custom task editor — define up to 50 tasks via the UI
- Protocol comparison — side-by-side metrics table with best-value highlighting
- PNG graph export — Gantt charts and comparison graphs saved to `output/`
- CSV / JSON export — full results exportable via CLI
- Filterable event log — search and filter by type across all protocols
- Demo mode — built-in 4-task scenario (L, H, M1, M2) that reproduces a classic inversion

---

## Example Output

### Metrics (PIP protocol)

```
Total Time:                  14 time units
Average Waiting Time:        1.67 time units
Average Turnaround Time:     4.33 time units
Average Response Time:       1.67 time units
CPU Utilization:             100.00%
Context Switches:            3
Priority Inversion Count:    1
Priority Inversion Duration: 1 time units
Throughput:                  0.2857 tasks/time unit
```

### Protocol Comparison

```
Metric                   None     PIP      PCP
Avg Waiting Time         2.67     1.67     1.67
Avg Turnaround Time      5.33     4.33     4.33
CPU Utilization (%)    100.00   100.00   100.00
Context Switches            3        3        3
Inversion Count             1        1        1
Inversion Duration          3        1        1
Throughput             0.3750   0.3750   0.3750
```

---

## CLI Usage

The legacy CLI is still available for headless / scripted use:

```bash
# Run default simulation
python main.py

# Run specific protocol
python main.py --protocol pip

# Compare all protocols with visualisation
python main.py --compare --visualize

# Generate random tasks
python main.py --generate 10 --protocol pcp --visualize

# Export results
python main.py --protocol pcp --metrics-report --export-all
```

### Programmatic usage

```python
from models import Task
from scheduler import Mutex
from simulation import Simulation

tasks = [
    Task('L', priority=1, arrival_time=0, execution_time=10, needs_resource=True),
    Task('H', priority=5, arrival_time=4, execution_time=2,  needs_resource=True),
]
mutex = Mutex(ceiling_priority=5)
results = Simulation(tasks, mutex, protocol='PIP').run()
```

---

## Future Improvements

- Multiple resources — support for multiple mutexes and complex dependencies
- Additional protocols — IPCP (Immediate Priority Ceiling), Stack Resource Policy
- Deadlock detection and prevention
- Advanced scheduling — EDF, Rate Monotonic Scheduling
- Real-time Gantt animation with WebSocket streaming
- Statistical analysis — Monte Carlo simulation over random task sets
- Unit test suite
- Dark mode for the dashboard

---

## References

1. Sha, L., Rajkumar, R., & Lehoczky, J. P. (1990). "Priority Inheritance Protocols: An Approach to Real-Time Synchronization." *IEEE Transactions on Computers*.
2. Liu, C. L., & Layland, J. W. (1973). "Scheduling Algorithms for Multiprogramming in a Hard-Real-Time Environment." *Journal of the ACM*.
3. Buttazzo, G. C. (2011). *Hard Real-Time Computing Systems*. Springer.
4. Reeves, G. (1997). "What Really Happened on Mars?" Microsoft Research.
5. Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). *Operating System Concepts*, 10th ed. Wiley.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

**Version:** 2.0.0 | **Status:** Active Development | **Last Updated:** 2026
