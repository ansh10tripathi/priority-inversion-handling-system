# Priority Inversion Handling System

[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()
[![Contributions](https://img.shields.io/badge/Contributions-Welcome-orange.svg)]()

A comprehensive simulation system for demonstrating and analyzing **priority inversion** in real-time operating systems, with implementations of Priority Inheritance Protocol (PIP) and Priority Ceiling Protocol (PCP).

---

## 📋 Table of Contents

- [Overview](#overview)
- [What is Priority Inversion?](#what-is-priority-inversion)
- [Protocols Implemented](#protocols-implemented)
- [Architecture](#architecture)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Example Output](#example-output)
- [Visualizations](#visualizations)
- [Project Structure](#project-structure)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This project simulates priority inversion scenarios in real-time operating systems and demonstrates how different protocols handle this critical scheduling anomaly. Built for educational purposes, it provides detailed metrics, visualizations, and comparative analysis of scheduling protocols.

**Key Highlights:**
- 🔄 Preemptive priority scheduling simulation
- 🛡️ Three protocol implementations (None, PIP, PCP)
- 📊 Comprehensive performance metrics
- 📈 Enhanced Gantt chart visualizations
- 🔍 Priority inversion detection and tracking
- 📁 Export results to CSV/JSON

---

## ⚠️ What is Priority Inversion?

**Priority inversion** is a scheduling anomaly where a high-priority task is indirectly blocked by a lower-priority task, violating the priority-based scheduling principle.

### How It Occurs

```
┌─────────────────────────────────────────────────────┐
│  Time 0: Low priority task (L) acquires mutex      │
│  Time 1: High priority task (H) needs mutex → BLOCKED
│  Time 2: Medium priority task (M) preempts L       │
│  Result: H waits for both M and L (INVERSION!)     │
└─────────────────────────────────────────────────────┘
```

### Real-World Impact

**Mars Pathfinder (1997):** NASA's Mars Pathfinder experienced system resets due to priority inversion. The issue was resolved by enabling Priority Inheritance Protocol in the VxWorks RTOS.

---

## 🔧 Protocols Implemented

### 1. No Protocol (Baseline)
- Standard preemptive priority scheduling
- No priority inversion handling
- Used as baseline for comparison

### 2. Priority Inheritance Protocol (PIP)
**Reactive approach:** When a high-priority task blocks on a resource, the owner temporarily inherits the higher priority.

**Advantages:**
- ✅ Simple implementation
- ✅ Only raises priority when needed
- ✅ Transparent to tasks

**Disadvantages:**
- ❌ Reactive (inversion must occur first)
- ❌ Potential for deadlock with multiple resources

### 3. Priority Ceiling Protocol (PCP)
**Proactive approach:** Each mutex has a ceiling priority. When a task acquires the mutex, its priority is immediately raised to the ceiling.

**Advantages:**
- ✅ Prevents priority inversion proactively
- ✅ More predictable behavior
- ✅ Prevents deadlock (with proper ceiling assignment)

**Disadvantages:**
- ❌ Requires knowledge of all tasks using resource
- ❌ May raise priority unnecessarily

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Priority Inversion System                 │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │ Models  │          │Scheduler│          │Simulation│
   │         │          │         │          │         │
   │  Task   │◄─────────│Scheduler│◄─────────│  Core   │
   └─────────┘          │  Mutex  │          │ Metrics │
                        │Protocols│          └────┬────┘
                        └─────────┘               │
                              │                   │
        ┌─────────────────────┼───────────────────┘
        │                     │
   ┌────▼────┐          ┌────▼──────┐
   │  Utils  │          │Visualization│
   │         │          │           │
   │Generator│          │   Gantt   │
   │Exporter │          │  Graphs   │
   └─────────┘          └───────────┘
```

### Module Responsibilities

| Module | Responsibility |
|--------|---------------|
| **models** | Task data structure and attributes |
| **scheduler** | Preemptive scheduling, mutex management, protocols |
| **simulation** | Orchestration, metrics collection, analysis |
| **utils** | Task generation, CSV/JSON export |
| **visualization** | Gantt charts, comparison graphs |

---

## ✨ Features

- ✅ **Preemptive Priority Scheduling** - Always runs highest priority ready task
- ✅ **Priority Inversion Detection** - Automatically detects when inversion occurs
- ✅ **Three Protocol Implementations** - None, PIP, PCP
- ✅ **Comprehensive Metrics** - 9 performance indicators
- ✅ **Enhanced Gantt Charts** - 4-state visualization (running, blocked, resource, priority change)
- ✅ **Comparison Graphs** - Automatic protocol comparison
- ✅ **Random Task Generation** - Configurable task generator
- ✅ **Export Functionality** - CSV and JSON export
- ✅ **CLI Interface** - Full command-line interface
- ✅ **Detailed Logging** - Step-by-step execution trace

---

## 📦 Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/priority-inversion-system.git
cd priority-inversion-system

# Install dependencies
pip install matplotlib

# Verify installation
python main.py --help
```

### Requirements

```
matplotlib>=3.5.0
```

---

## 🚀 Quick Start

### Run Default Simulation

```bash
python main.py
```

This runs all three protocols with default tasks and generates Gantt charts.

### Run Specific Protocol

```bash
python main.py --protocol pip
```

### Compare All Protocols

```bash
python main.py --compare --visualize
```

---

## 💡 Usage Examples

### Example 1: Basic Simulation with Visualization

```bash
python main.py --protocol pip --visualize
```

### Example 2: Generate Random Tasks

```bash
python main.py --generate 10 --protocol pcp --visualize
```

### Example 3: Priority Inversion Scenario

```bash
python main.py --generate 5 --inversion-scenario --compare --visualize
```

### Example 4: Full Analysis with Export

```bash
python main.py --protocol pcp --metrics-report --export-all
```

### Example 5: Custom Configuration

```bash
python main.py --generate 8 --max-priority 10 --resource-prob 0.7 --protocol pip
```

### Programmatic Usage

```python
from models import Task
from scheduler import Mutex
from simulation import Simulation
from visualization import plot_gantt_chart

# Create tasks
tasks = [
    Task('T1', priority=3, arrival_time=0, execution_time=5, needs_resource=True),
    Task('T2', priority=1, arrival_time=1, execution_time=3, needs_resource=False)
]

# Run simulation
mutex = Mutex(ceiling_priority=3)
sim = Simulation(tasks, mutex, protocol='PIP')
results = sim.run()

# Visualize
plot_gantt_chart(results['timeline'], tasks, 'PIP')
```

---

## 📊 Example Output

### Console Output

```
============================================================
Performance Metrics - PIP Protocol
============================================================
Total Time:                  8 time units
Average Waiting Time:        1.67 time units
Average Turnaround Time:     4.33 time units
Average Response Time:       1.67 time units
CPU Utilization:             100.00%
Context Switches:            3
Priority Inversion Count:    1
Priority Inversion Duration: 1 time units
Throughput:                  0.3750 tasks/time unit
```

### Comparison Table

```
====================================================================================================
Protocol Comparison Report
====================================================================================================

Metric                                    None                 PIP                 PCP
----------------------------------------------------------------------------------------------------
Total Time                                   8                   8                   8
Avg Waiting Time                          2.67                1.67                1.67
Avg Turnaround Time                       5.33                4.33                4.33
CPU Utilization (%)                     100.00              100.00              100.00
Context Switches                             3                   3                   3
Inversion Count                              1                   1                   1
Inversion Duration                           3                   1                   1
Throughput                              0.3750              0.3750              0.3750
```

---

## 📸 Visualizations

### Enhanced Gantt Chart

The system generates color-coded Gantt charts showing:
- 🔵 **Blue** - Task running (normal)
- 🟠 **Orange** - Task running (holding resource)
- 🟣 **Purple** - Task running (priority changed)
- 🔴 **Red** - Task blocked (waiting for resource)

![Gantt Chart Example](gantt_pip.png)

### Comparison Graphs

Automatic generation of 4 comparison graphs:
1. Average Waiting Time
2. Average Turnaround Time
3. Context Switches
4. Priority Inversion Duration

![Comparison Graph](comparison_waiting_time.png)

---

## 📁 Project Structure

```
priority_inversion_system/
│
├── main.py                          # Entry point with CLI
│
├── models/                          # Data models
│   ├── __init__.py
│   └── task.py                      # Task class
│
├── scheduler/                       # Scheduling components
│   ├── __init__.py
│   ├── scheduler.py                 # Preemptive priority scheduler
│   ├── mutex.py                     # Mutex resource management
│   └── protocols.py                 # PIP and PCP implementations
│
├── simulation/                      # Simulation engine
│   ├── __init__.py
│   ├── simulation.py                # Simulation orchestration
│   └── metrics.py                   # Performance metrics
│
├── utils/                           # Utility modules
│   ├── __init__.py
│   ├── task_generator.py            # Random task generation
│   └── exporter.py                  # CSV/JSON export
│
├── visualization/                   # Visualization components
│   ├── __init__.py
│   ├── gantt_chart.py               # Gantt chart generation
│   └── performance_graphs.py        # Comparison graphs
│
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
```

---

## 🔮 Future Improvements

### Planned Features

- [ ] **Multiple Resources** - Support for multiple mutexes and complex dependencies
- [ ] **Additional Protocols** - Immediate Priority Ceiling Protocol (IPCP), Stack Resource Policy (SRP)
- [ ] **Deadlock Detection** - Implement deadlock detection and prevention
- [ ] **Advanced Scheduling** - EDF (Earliest Deadline First), RMS (Rate Monotonic Scheduling)
- [ ] **Interactive Visualization** - Real-time animation of scheduling
- [ ] **Web Interface** - Browser-based simulation interface
- [ ] **Statistical Analysis** - Monte Carlo simulation with random task sets
- [ ] **RTOS Integration** - Interface with real-time operating systems
- [ ] **Performance Optimization** - Faster simulation for large task sets
- [ ] **Unit Tests** - Comprehensive test coverage

### Enhancement Ideas

- 🎨 Dark mode for visualizations
- 📱 Mobile-friendly web interface
- 🔊 Audio alerts for priority inversions
- 📝 LaTeX report generation
- 🌐 Multi-language support
- 🎓 Tutorial mode for learning

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide
- Add docstrings to all functions
- Include unit tests for new features
- Update documentation as needed

---

<!-- ## 📚 Documentation

- [Project Report](PROJECT_REPORT.md) - Comprehensive technical documentation
- [Viva Questions](VIVA_QUESTIONS.md) - Q&A for presentations
- [CLI Documentation](CLI_DOCUMENTATION.md) - Complete CLI reference
- [Refactoring Summary](REFACTORING_SUMMARY.md) - Architecture details
- [Quick Reference](MODULAR_STRUCTURE_QUICKREF.md) - Import guide -->

<!-- --- -->

## 📖 References

1. Sha, L., Rajkumar, R., & Lehoczky, J. P. (1990). "Priority Inheritance Protocols: An Approach to Real-Time Synchronization." *IEEE Transactions on Computers*.

2. Liu, C. L., & Layland, J. W. (1973). "Scheduling Algorithms for Multiprogramming in a Hard-Real-Time Environment." *Journal of the ACM*.

3. Buttazzo, G. C. (2011). "Hard Real-Time Computing Systems: Predictable Scheduling Algorithms and Applications." Springer.

4. Reeves, G. (1997). "What Really Happened on Mars?" Microsoft Research.

5. Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). "Operating System Concepts." Wiley, 10th Edition.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

**Priority Inversion Handling System Development Team**

- Developed for Operating Systems Course Project
- Inspired by the Mars Pathfinder incident
- Based on research by Sha, Rajkumar, and Lehoczky

---

## 🙏 Acknowledgments

- Inspired by NASA's Mars Pathfinder priority inversion incident
- Based on seminal research in real-time scheduling
- Built for educational purposes in Operating Systems courses
- Thanks to the open-source community for tools and libraries

---

## 📞 Support

For questions, issues, or suggestions:

- 📧 Open an issue on GitHub
- 💬 Start a discussion in the repository
- 📖 Check the documentation files

---

## ⭐ Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Last Updated:** 2026

**Status:** Active Development

**Version:** 1.0.0
