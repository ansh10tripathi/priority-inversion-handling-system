import { useState, useEffect, useRef } from "react";
import axios from "axios";
import DashboardPage  from "./pages/DashboardPage";
import SimulationPage from "./pages/SimulationPage";
import MetricsPage    from "./pages/MetricsPage";
import LogsPage       from "./pages/LogsPage";
import TasksPage      from "./pages/TasksPage";

const API       = "http://127.0.0.1:8000";
const PROTOCOLS = ["None", "PIP", "PCP"];
const SESSION   = "default";

const NAV = [
  { icon: "▦", label: "Dashboard"  },
  { icon: "⏱", label: "Simulation" },
  { icon: "📊", label: "Metrics"   },
  { icon: "📋", label: "Logs"      },
  { icon: "✚", label: "Tasks"      },
];

const DEMO_TASKS = [
  { id: "demo-1", name: "L",  priority: 1, arrival: 0, execution: 10, needs_resource: true  },
  { id: "demo-2", name: "H",  priority: 5, arrival: 4, execution: 2,  needs_resource: true  },
  { id: "demo-3", name: "M1", priority: 3, arrival: 1, execution: 4,  needs_resource: false },
  { id: "demo-4", name: "M2", priority: 4, arrival: 2, execution: 3,  needs_resource: false },
];

// ── Sidebar ───────────────────────────────────────────────────────────────────

function Sidebar({
  activePage, onNavigate,
  protocol, onProtocolChange,
  allResults, loading,
  stepMode, stepStarted, stepDone,
  onRun, onStep, onReset, onSetStepMode, onViewResults,
  customTasks,
}) {
  const anyInversions = PROTOCOLS.some(
    p => (allResults[p]?.metrics?.priority_inversion_count ?? 0) > 0
  );
  const totalInversions = PROTOCOLS.reduce(
    (sum, p) => sum + (allResults[p]?.metrics?.priority_inversion_count ?? 0), 0
  );

  return (
    <aside style={{
      width: 220, flexShrink: 0,
      background: "var(--sidebar)",
      display: "flex", flexDirection: "column",
      padding: "28px 0 24px",
      position: "sticky", top: 0, height: "100vh", overflowY: "auto",
    }}>
      {/* Logo */}
      <div style={{ padding: "0 20px 28px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 34, height: 34, borderRadius: 9,
            background: "rgba(255,255,255,0.2)",
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16,
          }}>⚙</div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: "#fff", lineHeight: 1.2 }}>PIS</div>
            <div style={{ fontSize: 10, color: "rgba(255,255,255,0.6)" }}>Simulator</div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: "0 10px", display: "flex", flexDirection: "column", gap: 2 }}>
        {NAV.map((item, i) => (
          <button
            key={item.label}
            onClick={() => onNavigate(i)}
            style={{
              display: "flex", alignItems: "center", gap: 10,
              padding: "9px 12px", borderRadius: 8, border: "none",
              background: activePage === i ? "rgba(255,255,255,0.18)" : "transparent",
              color: activePage === i ? "#fff" : "rgba(255,255,255,0.65)",
              fontSize: 13, fontWeight: activePage === i ? 600 : 400,
              cursor: "pointer", textAlign: "left", width: "100%",
              transition: "background 0.15s, color 0.15s",
            }}
          >
            <span style={{ fontSize: 14 }}>{item.icon}</span>
            {item.label}
            {i === 0 && anyInversions && (
              <span style={{ marginLeft: "auto", fontSize: 10, fontWeight: 700, background: "#E57373", color: "#fff", borderRadius: 10, padding: "1px 6px" }}>
                {totalInversions}
              </span>
            )}
            {i === 4 && customTasks.length > 0 && !customTasks.every((t, i2) => DEMO_TASKS[i2] && t.name === DEMO_TASKS[i2].name) && (
              <span style={{ marginLeft: "auto", fontSize: 10, fontWeight: 700, background: "#4F9CF9", color: "#fff", borderRadius: 10, padding: "1px 6px" }}>
                {customTasks.length}
              </span>
            )}
          </button>
        ))}
      </nav>

      {/* Controls */}
      <div style={{ padding: "20px 14px 0", display: "flex", flexDirection: "column", gap: 12 }}>
        <div style={{ height: 1, background: "rgba(255,255,255,0.15)", margin: "0 0 4px" }} />

        {/* Protocol selector — only relevant for step mode */}
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          <span style={{ fontSize: 11, fontWeight: 600, color: "rgba(255,255,255,0.6)", textTransform: "uppercase", letterSpacing: "0.07em" }}>
            Protocol
          </span>
          <select
            className="proto-select"
            value={protocol}
            onChange={(e) => onProtocolChange(e.target.value)}
            disabled={loading || stepStarted}
            style={{ width: "100%" }}
          >
            {PROTOCOLS.map(p => (
              <option key={p} value={p}>{p === "None" ? "None (baseline)" : p}</option>
            ))}
          </select>
        </div>

        {/* Mode toggle */}
        <div className="mode-toggle">
          <button className={`mode-btn${!stepMode ? " active" : ""}`} onClick={() => { if (stepMode) onReset(); }}>
            Full Run
          </button>
          <button className={`mode-btn${stepMode ? " active" : ""}`} onClick={() => { if (!stepMode) onSetStepMode(true); }}>
            Step
          </button>
        </div>

        {/* Action button */}
        {!stepMode ? (
          <button className="run-btn" onClick={onRun} disabled={loading} style={{ width: "100%", justifyContent: "center" }}>
            {loading ? <><span className="spinner" /> Running…</> : <>▶ Run All Protocols</>}
          </button>
        ) : (
          <>
            {stepDone ? (
              <button
                className="run-btn"
                onClick={onViewResults}
                style={{ width: "100%", justifyContent: "center", background: "#4CAF50", boxShadow: "0 2px 8px rgba(76,175,80,0.3)", cursor: "pointer" }}
              >
                📊 View Results
              </button>
            ) : (
              <button
                className="run-btn"
                onClick={onStep}
                disabled={loading}
                style={{ width: "100%", justifyContent: "center", background: "var(--accent)", boxShadow: "0 2px 8px rgba(79,156,249,0.35)" }}
              >
                {loading ? <><span className="spinner" /> Stepping…</>
                  : !stepStarted ? "⏭ Start Stepping"
                  : "⏭ Next Step"}
              </button>
            )}
            {stepStarted && (
              <button className="reset-btn" onClick={onReset} style={{ width: "100%", justifyContent: "center" }}>
                ✕ Reset
              </button>
            )}
          </>
        )}

        {/* Run status summary */}
        <div style={{ marginTop: 4, background: "rgba(255,255,255,0.12)", borderRadius: 8, padding: "8px 12px" }}>
          <div style={{ fontSize: 10, fontWeight: 600, color: "rgba(255,255,255,0.5)", textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: 6 }}>
            Protocol Status
          </div>
          {PROTOCOLS.map(p => {
            const done = !!allResults[p];
            return (
              <div key={p} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 4 }}>
                <span style={{ fontSize: 11, color: "rgba(255,255,255,0.75)", fontWeight: 600 }}>{p === "None" ? "None" : p}</span>
                <span style={{
                  fontSize: 9, fontWeight: 700, borderRadius: 10, padding: "1px 7px",
                  background: done ? "rgba(76,175,80,0.25)" : "rgba(255,255,255,0.1)",
                  color: done ? "#81C784" : "rgba(255,255,255,0.4)",
                }}>
                  {done ? "✓ Done" : "Not Run"}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </aside>
  );
}

// ── Topbar ────────────────────────────────────────────────────────────────────

function Topbar({ pageName, stepMode, stepStarted, stepDone, customTasks }) {
  const isDemoSet = customTasks.length === DEMO_TASKS.length &&
    customTasks.every((t, i) => t.name === DEMO_TASKS[i].name);
  const subtitle = customTasks.map(t => `${t.name}(P=${t.priority})`).join(" ");
  return (
    <header style={{
      background: "var(--surface)", borderBottom: "1px solid var(--border)",
      padding: "14px 28px", display: "flex", alignItems: "center",
      justifyContent: "space-between", position: "sticky", top: 0, zIndex: 10,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: 16, fontWeight: 700, color: "var(--text)" }}>
            {pageName}
          </h1>
          <p style={{ margin: "2px 0 0", fontSize: 11, color: "var(--text-sec)", fontFamily: "Consolas, monospace" }}>
            {subtitle || "No tasks loaded"}
          </p>
        </div>
        {isDemoSet ? (
          <span style={{ fontSize: 10, fontWeight: 700, color: "#92400E", background: "#FEF3C7", border: "1px solid #FCD34D", borderRadius: 20, padding: "3px 10px", whiteSpace: "nowrap" }}>
            🎯 Demo Mode
          </span>
        ) : (
          <span style={{ fontSize: 10, fontWeight: 700, color: "#1D4ED8", background: "#EFF6FF", border: "1px solid #BFDBFE", borderRadius: 20, padding: "3px 10px", whiteSpace: "nowrap" }}>
            ✚ Custom Tasks ({customTasks.length})
          </span>
        )}
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        {stepMode && stepStarted && !stepDone && (
          <span style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "#4F9CF9", fontWeight: 600, background: "#EFF6FF", border: "1px solid #BFDBFE", borderRadius: 20, padding: "3px 10px" }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#4F9CF9", animation: "spin 1.5s linear infinite", display: "inline-block" }} />
            Stepping
          </span>
        )}
        {stepDone && (
          <span style={{ fontSize: 11, color: "#166534", fontWeight: 600, background: "#F0FDF4", border: "1px solid #BBF7D0", borderRadius: 20, padding: "3px 10px" }}>
            ✓ Simulation Complete
          </span>
        )}
        <div style={{ width: 32, height: 32, borderRadius: "50%", background: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, color: "#fff", fontWeight: 700 }}>U</div>
      </div>
    </header>
  );
}

// ── App ───────────────────────────────────────────────────────────────────────

export default function App() {
  const [activePage,     setActivePage]     = useState(0);
  const [selectedProtocol, setSelectedProtocol] = useState("None"); // single-run + step mode
  const [viewProtocol,   setViewProtocol]   = useState("None"); // which protocol to display
  const [loading,     setLoading]     = useState(false);
  const [error,       setError]       = useState(null);
  const [customTasks, setCustomTasks] = useState(DEMO_TASKS);
  const [graphsKey,   setGraphsKey]   = useState(null);

  // allResults: { None: {timeline, metrics, logs} | null, PIP: ..., PCP: ... }
  const [allResults, setAllResults] = useState({ None: null, PIP: null, PCP: null });

  // Step mode state
  const [stepMode,       setStepMode]       = useState(false);
  const [stepStarted,    setStepStarted]    = useState(false);
  const [stepDone,       setStepDone]       = useState(false);
  const [stepTimeline,   setStepTimeline]   = useState([]);
  const [stepLogs,       setStepLogs]       = useState([]);
  const [stepMetrics,    setStepMetrics]    = useState(null);
  const [schedulerState, setSchedulerState] = useState(null);

  // Speed control — ref mirrors state so the auto-play loop never reads a stale value
  const [stepSpeed,  setStepSpeed]  = useState(700);
  const stepSpeedRef                = useRef(700);
  const [autoPlaying, setAutoPlaying] = useState(false);
  const autoPlayRef                 = useRef(false); // abort flag for the loop

  useEffect(() => { handleLoadDemo(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  function handleLoadDemo() {
    handleReset();
    setCustomTasks(DEMO_TASKS);
  }

  // ── Single-protocol run ──
  async function handleRunSingle(p = selectedProtocol) {
    if (loading) return;
    setLoading(true);
    setError(null);
    setStepMode(false);
    try {
      const { data } = await axios.post(`${API}/simulate`, { protocol: p, tasks: customTasks });
      setAllResults(prev => ({
        ...prev,
        [p]: { timeline: data.timeline, metrics: data.metrics, logs: data.logs },
      }));
      setViewProtocol(p);
      generateGraphs(customTasks);
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message ?? "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  // ── Run ALL 3 protocols in parallel ──
  async function handleRunAll() {
    if (loading) return;
    setLoading(true);
    setError(null);
    setStepMode(false);
    setAllResults({ None: null, PIP: null, PCP: null });
    try {
      const requests = PROTOCOLS.map(p =>
        axios.post(`${API}/simulate`, { protocol: p, tasks: customTasks })
          .then(res => ({ protocol: p, data: res.data }))
          .catch(err => ({ protocol: p, error: err.response?.data?.detail ?? err.message }))
      );
      const responses = await Promise.all(requests);
      const newResults = { None: null, PIP: null, PCP: null };
      let firstError = null;
      for (const { protocol: p, data, error: e } of responses) {
        if (e) { firstError = firstError ?? `${p}: ${e}`; continue; }
        newResults[p] = { timeline: data.timeline, metrics: data.metrics, logs: data.logs };
      }
      setAllResults(newResults);
      if (firstError) setError(firstError);
      // After run-all, display whichever protocol the user had selected
      setViewProtocol(selectedProtocol);
      generateGraphs(customTasks);
    } catch (err) {
      setError(err.message ?? "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  function handleSpeedChange(ms) {
    stepSpeedRef.current = ms;
    setStepSpeed(ms);
  }

  // ── Auto-play: runs steps automatically with stepSpeed delay between each ──
  async function handleAutoPlay() {
    if (autoPlaying) {
      // Pause: set abort flag, loop will exit after current step
      autoPlayRef.current = false;
      setAutoPlaying(false);
      return;
    }
    autoPlayRef.current = true;
    setAutoPlaying(true);

    // If not yet started, initialise the session first
    if (!stepStarted) {
      setLoading(true);
      setError(null);
      setStepTimeline([]);
      setStepLogs([]);
      setStepMetrics(null);
      setSchedulerState(null);
      setStepDone(false);
      setStepMode(true);
      try {
        await axios.post(`${API}/step/init`, { tasks: customTasks }, { params: { protocol: selectedProtocol, session_id: SESSION } });
        setStepStarted(true);
      } catch (err) {
        setError(err.response?.data?.detail ?? err.message ?? "Unknown error");
        autoPlayRef.current = false;
        setAutoPlaying(false);
        setLoading(false);
        return;
      }
      setLoading(false);
    }

    // Step loop — reads stepSpeedRef so slider changes take effect immediately
    while (autoPlayRef.current) {
      setLoading(true);
      let done = false;
      try {
        const { data } = await axios.post(`${API}/step/next`, null, { params: { session_id: SESSION } });
        applyStepData(data, customTasks);
        done = data.done;
      } catch (err) {
        setError(err.response?.data?.detail ?? err.message ?? "Unknown error");
        break;
      } finally {
        setLoading(false);
      }
      if (done) break;
      // Delay between steps — uses ref so it always reflects the latest slider value
      await new Promise(resolve => setTimeout(resolve, stepSpeedRef.current));
    }

    autoPlayRef.current = false;
    setAutoPlaying(false);
  }

  // ── Step mode (single manual step) ──
  async function handleStep() {
    if (loading) return;
    setLoading(true);
    setError(null);
    try {
      if (!stepStarted) {
        setStepTimeline([]);
        setStepLogs([]);
        setStepMetrics(null);
        setSchedulerState(null);
        setStepDone(false);
        setStepMode(true);
        await axios.post(`${API}/step/init`, { tasks: customTasks }, { params: { protocol: selectedProtocol, session_id: SESSION } });
        setStepStarted(true);
        const { data } = await axios.post(`${API}/step/next`, null, { params: { session_id: SESSION } });
        applyStepData(data, customTasks);
      } else {
        const { data } = await axios.post(`${API}/step/next`, null, { params: { session_id: SESSION } });
        applyStepData(data, customTasks);
      }
    } catch (err) {
      setError(err.response?.data?.detail ?? err.message ?? "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  function applyStepData(data, taskSnapshot) {
    if (data.tick) setStepTimeline(prev => [...prev, data.tick]);
    if (data.new_logs?.length) setStepLogs(prev => [...prev, ...data.new_logs]);
    setSchedulerState({
      currentTime: data.current_time,
      running:     data.tick?.task ?? null,
      ready:       data.ready   ?? [],
      blocked:     data.blocked ?? [],
      mutexOwner:  data.mutex_owner ?? null,
    });
    if (data.done) {
      setStepDone(true);
      setStepMetrics(data.metrics);
      setStepTimeline(data.timeline ?? []);
      setStepLogs(data.logs ?? []);
      // Store step result under its protocol
      setAllResults(prev => ({
        ...prev,
        [selectedProtocol]: { timeline: data.timeline, metrics: data.metrics, logs: data.logs },
      }));
      setViewProtocol(selectedProtocol);
      generateGraphs(taskSnapshot);
    }
  }

  async function generateGraphs(tasks) {
    try {
      await axios.post(`${API}/generate-graphs`, { tasks });
      setGraphsKey(Date.now());
    } catch (_) {}
  }

  function handleReset() {
    axios.delete(`${API}/step/reset`, { params: { session_id: SESSION } }).catch(() => {});
    autoPlayRef.current = false;   // stop any running auto-play loop
    setAutoPlaying(false);
    setStepMode(false);
    setStepStarted(false);
    setStepDone(false);
    setStepTimeline([]);
    setStepLogs([]);
    setStepMetrics(null);
    setSchedulerState(null);
    setError(null);
    setLoading(false);
  }

  const stepSimResult = stepMode
    ? { protocol: selectedProtocol, timeline: stepTimeline, metrics: stepMetrics, logs: stepLogs }
    : allResults[viewProtocol];

  const pageNames = ["Dashboard", "Simulation", "Metrics", "Logs", "Tasks"];

  return (
    <div style={{ minHeight: "100vh", display: "flex", background: "var(--bg)" }}>
      <Sidebar
        activePage={activePage}
        onNavigate={setActivePage}
        protocol={selectedProtocol}
        onProtocolChange={setSelectedProtocol}
        allResults={allResults}
        loading={loading}
        stepMode={stepMode}
        stepStarted={stepStarted}
        stepDone={stepDone}
        onRun={handleRunAll}
        onStep={handleStep}
        onReset={handleReset}
        onSetStepMode={setStepMode}
        onViewResults={() => setActivePage(2)}
        customTasks={customTasks}
      />

      <div style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
        <Topbar
          pageName={pageNames[activePage]}
          stepMode={stepMode}
          stepStarted={stepStarted}
          stepDone={stepDone}
          customTasks={customTasks}
        />

        <main style={{ flex: 1, padding: "24px 28px", display: "flex", flexDirection: "column", gap: 20 }}>
          {error && <div className="error-banner">⚠ {error}</div>}

          {activePage === 0 && (
            <DashboardPage
              allResults={allResults}
              viewProtocol={viewProtocol}
              onViewProtocolChange={setViewProtocol}
            />
          )}
          {activePage === 1 && (
            <SimulationPage
              selectedProtocol={selectedProtocol}
              onSelectedProtocolChange={setSelectedProtocol}
              viewProtocol={stepMode ? selectedProtocol : viewProtocol}
              onViewProtocolChange={setViewProtocol}
              loading={loading}
              simResult={stepSimResult}
              stepMode={stepMode}
              stepStarted={stepStarted}
              stepDone={stepDone}
              schedulerState={schedulerState}
              onRunSingle={handleRunSingle}
              onRunAll={handleRunAll}
              onStep={handleStep}
              onAutoPlay={handleAutoPlay}
              autoPlaying={autoPlaying}
              stepSpeed={stepSpeed}
              onSpeedChange={handleSpeedChange}
              onReset={handleReset}
              onSetStepMode={setStepMode}
              onViewResults={() => setActivePage(2)}
              activeTasks={customTasks}
              allResults={allResults}
              onNavigateToDashboard={() => setActivePage(0)}
            />
          )}
          {activePage === 2 && (
            <MetricsPage
              allResults={allResults}
              viewProtocol={viewProtocol}
              onViewProtocolChange={setViewProtocol}
              graphsKey={graphsKey}
            />
          )}
          {activePage === 3 && (
            <LogsPage
              allResults={allResults}
              viewProtocol={viewProtocol}
              onViewProtocolChange={setViewProtocol}
            />
          )}
          {activePage === 4 && (
            <TasksPage
              tasks={customTasks}
              onTasksChange={setCustomTasks}
              onLoadDemo={handleLoadDemo}
              isActive={!customTasks.every((t, i2) => DEMO_TASKS[i2] && t.name === DEMO_TASKS[i2].name)}
            />
          )}
        </main>
      </div>
    </div>
  );
}
