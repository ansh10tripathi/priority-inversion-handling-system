// pages/SimulationPage.js
import { useState, useEffect, useRef } from "react";
import GanttChart from "../GanttChart";

const PROTOCOLS = ["None", "PIP", "PCP"];

const PROTO_META = {
  None: { color: "#9CA3AF", label: "None — Baseline" },
  PIP:  { color: "#4F9CF9", label: "PIP — Priority Inheritance" },
  PCP:  { color: "#6B8F71", label: "PCP — Priority Ceiling" },
};

// ── Speed slider ─────────────────────────────────────────────────────────────

function SpeedSlider({ speed, onChange }) {
  const MIN = 100, MAX = 1500;
  // Invert: right = faster (lower ms)
  const fillPct = ((MAX - speed) / (MAX - MIN)) * 100;
  const label = speed <= 200 ? "Fast" : speed <= 600 ? "Normal" : speed <= 1100 ? "Slow" : "Very Slow";

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <span style={{
        fontSize: 11, fontWeight: 600, color: "var(--text-dim)",
        textTransform: "uppercase", letterSpacing: "0.07em", whiteSpace: "nowrap",
      }}>
        Speed
      </span>
      <span style={{ fontSize: 10, color: "var(--text-dim)", whiteSpace: "nowrap" }}>Slow</span>

      {/* Track wrapper — padding keeps the thumb fully visible */}
      <div style={{ flex: 1, minWidth: 100, maxWidth: 180, position: "relative", height: 20, display: "flex", alignItems: "center" }}>
        {/* Grey base track */}
        <div style={{
          position: "absolute", left: 0, right: 0,
          height: 4, borderRadius: 2, background: "var(--border2)",
        }} />
        {/* Coloured fill — right-to-left because right = faster */}
        <div style={{
          position: "absolute", right: 0,
          height: 4, borderRadius: 2,
          width: `${100 - fillPct}%`,
          background: "var(--border2)",
        }} />
        <div style={{
          position: "absolute", left: 0,
          height: 4, borderRadius: 2,
          width: `${fillPct}%`,
          background: "var(--primary-dk)",
        }} />
        <input
          type="range"
          min={MIN} max={MAX} step={50}
          value={speed}
          onChange={e => onChange(Number(e.target.value))}
          style={{
            position: "relative", zIndex: 1,
            width: "100%", margin: 0,
            WebkitAppearance: "none", appearance: "none",
            background: "transparent", cursor: "pointer",
            accentColor: "var(--primary-dk)",
          }}
        />
      </div>

      <span style={{ fontSize: 10, color: "var(--text-dim)", whiteSpace: "nowrap" }}>Fast</span>
      <span style={{
        fontSize: 10, fontWeight: 700, borderRadius: 8, padding: "2px 8px",
        whiteSpace: "nowrap", minWidth: 80, textAlign: "center",
        background: "var(--surface2)", color: "var(--text-sec)",
        border: "1px solid var(--border)", fontVariantNumeric: "tabular-nums",
      }}>
        {speed}ms·{label}
      </span>
    </div>
  );
}

// ── SchedulerState (step mode live panel) ─────────────────────────────────────

function SchedulerState({ state }) {
  if (!state) return null;
  const { currentTime, running, ready, blocked, mutexOwner } = state;

  const badge = (label, bg, color) => (
    <span className="sched-badge" style={{ background: bg, color, marginRight: 4 }}>
      {label}
    </span>
  );

  return (
    <div className="inner-card" style={{ display: "flex", flexWrap: "wrap", gap: 14, alignItems: "center" }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 6 }}>
        <span style={{ fontSize: 11, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Time</span>
        <strong style={{ fontSize: 22, color: "var(--text)", fontVariantNumeric: "tabular-nums" }}>{currentTime}</strong>
      </div>
      <div style={{ width: 1, height: 24, background: "var(--border)" }} />
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <span style={{ fontSize: 10, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Running</span>
        {running ? badge(running, "#F0FDF4", "#166534") : <span style={{ fontSize: 11, color: "var(--text-dim)" }}>idle</span>}
      </div>
      {ready.length > 0 && (
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ fontSize: 10, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Ready</span>
          {ready.map(t => badge(`${t.id} P=${t.priority}`, "#EFF6FF", "#1D4ED8"))}
        </div>
      )}
      {blocked.length > 0 && (
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ fontSize: 10, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Blocked</span>
          {blocked.map(t => badge(`${t.id} P=${t.priority}`, "#FFF8F0", "#C2410C"))}
        </div>
      )}
      {mutexOwner && (
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span style={{ fontSize: 10, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Mutex</span>
          {badge(mutexOwner, "#FAF5FF", "#7E22CE")}
        </div>
      )}
    </div>
  );
}

// ── Protocol selector row ─────────────────────────────────────────────────────

function ProtocolSelector({ selectedProtocol, onChange, allResults, loading, disabled }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
      <span style={{ fontSize: 11, fontWeight: 600, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.07em", whiteSpace: "nowrap" }}>
        Protocol
      </span>
      <div style={{ display: "flex", gap: 6 }}>
        {PROTOCOLS.map(p => {
          const meta   = PROTO_META[p];
          const done   = !!allResults[p];
          const active = selectedProtocol === p;
          return (
            <button
              key={p}
              onClick={() => onChange(p)}
              disabled={disabled}
              style={{
                padding: "5px 14px", borderRadius: 8, border: "2px solid",
                fontSize: 12, fontWeight: 600, cursor: disabled ? "not-allowed" : "pointer",
                transition: "all 0.15s",
                borderColor: active ? meta.color : "var(--border)",
                background:  active ? meta.color + "18" : "var(--surface)",
                color:       active ? meta.color : "var(--text-sec)",
              }}
            >
              {p === "None" ? "None" : p}
              {/* status dot */}
              <span style={{
                display: "inline-block", width: 6, height: 6, borderRadius: "50%",
                marginLeft: 6, verticalAlign: "middle",
                background: done ? "#4CAF50" : "var(--border2)",
              }} />
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ── Gantt section — animates tick-by-tick at slider speed ───────────────────────

function GanttSection({ viewProtocol, allResults, simResult, stepMode, stepStarted, stepDone, stepSpeed }) {
  const meta         = PROTO_META[viewProtocol];
  const isLive       = stepMode && stepStarted && !stepDone;

  // The full timeline for the currently viewed protocol
  const fullTimeline = stepMode
    ? simResult?.timeline
    : allResults[viewProtocol]?.timeline;

  const hasResult    = !!fullTimeline?.length;

  // visibleCount: how many ticks of fullTimeline are currently shown
  const [visibleCount, setVisibleCount] = useState(0);
  const intervalRef                     = useRef(null);
  const prevTimelineRef                 = useRef(null);

  useEffect(() => {
    // In live step mode the timeline grows one tick at a time already — show all
    if (isLive) {
      setVisibleCount(fullTimeline?.length ?? 0);
      return;
    }

    // No timeline yet
    if (!fullTimeline?.length) {
      setVisibleCount(0);
      prevTimelineRef.current = null;
      return;
    }

    // Same timeline reference — nothing changed, don’t restart
    if (fullTimeline === prevTimelineRef.current) return;
    prevTimelineRef.current = fullTimeline;

    // New timeline arrived — clear any running interval and restart from tick 0
    clearInterval(intervalRef.current);
    setVisibleCount(0);

    let count = 0;
    const total = fullTimeline.length;

    intervalRef.current = setInterval(() => {
      count += 1;
      setVisibleCount(count);
      if (count >= total) clearInterval(intervalRef.current);
    }, stepSpeed);          // stepSpeed is read at interval-creation time

    return () => clearInterval(intervalRef.current);
  // Re-run when the timeline itself changes or when stepSpeed changes mid-animation
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fullTimeline, stepSpeed, isLive]);

  // When stepSpeed changes while an animation is already running, restart it
  // from the current position so the new speed takes effect immediately
  useEffect(() => {
    if (!intervalRef.current) return;          // no animation running
    if (!fullTimeline?.length) return;
    if (isLive) return;

    clearInterval(intervalRef.current);
    let count = visibleCount;
    const total = fullTimeline.length;
    if (count >= total) return;

    intervalRef.current = setInterval(() => {
      count += 1;
      setVisibleCount(count);
      if (count >= total) clearInterval(intervalRef.current);
    }, stepSpeed);

    return () => clearInterval(intervalRef.current);
  // Only re-run when stepSpeed changes, not on every visibleCount tick
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stepSpeed]);

  const displayTimeline = fullTimeline?.slice(0, visibleCount) ?? [];
  const animating       = hasResult && visibleCount < (fullTimeline?.length ?? 0);

  return (
    <div className="card">
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
        <p className="card-title" style={{ margin: 0 }}>
          Gantt Chart — {viewProtocol}
          {isLive && <span style={{ marginLeft: 8, fontSize: 10, color: "#4F9CF9", fontWeight: 500 }}>● live</span>}
          {animating && !isLive && (
            <span style={{ marginLeft: 8, fontSize: 10, color: "#F97316", fontWeight: 500 }}>
              ● {visibleCount} / {fullTimeline.length} ticks
            </span>
          )}
        </p>
        <span style={{
          fontSize: 10, fontWeight: 700, borderRadius: 10, padding: "3px 10px",
          background: animating ? "#FFF8F0" : hasResult ? "#F0FDF4" : "var(--surface2)",
          color:      animating ? "#C2410C" : hasResult ? "#166534" : "var(--text-dim)",
          border:     animating ? "1px solid #FDBA74" : hasResult ? "1px solid #BBF7D0" : "1px solid var(--border)",
        }}>
          {animating ? "▶ Animating…" : hasResult ? "✓ Completed" : "Not Run Yet"}
        </span>
      </div>

      {/* Protocol strip */}
      <div style={{
        display: "flex", alignItems: "center", gap: 8,
        padding: "6px 10px", borderRadius: 6, marginBottom: 12,
        background: meta.color + "12", border: `1px solid ${meta.color}33`,
      }}>
        <span style={{ width: 8, height: 8, borderRadius: "50%", background: meta.color, flexShrink: 0 }} />
        <span style={{ fontSize: 11, color: meta.color, fontWeight: 600 }}>{meta.label}</span>
      </div>

      {!hasResult && !isLive ? (
        <div style={{ padding: "40px 0", textAlign: "center", display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 28 }}>⏳</span>
          <span style={{ fontSize: 13, color: "var(--text-dim)", fontWeight: 500 }}>
            {viewProtocol} has not been run yet
          </span>
          <span style={{ fontSize: 11, color: "var(--text-dim)" }}>
            Select it above and click <strong>▶ Run</strong> to execute
          </span>
        </div>
      ) : (
        <GanttChart timeline={displayTimeline.length ? displayTimeline : fullTimeline} />
      )}
    </div>
  );
}

// ── SimulationPage ────────────────────────────────────────────────────────────

export default function SimulationPage({
  selectedProtocol, onSelectedProtocolChange,
  viewProtocol, onViewProtocolChange,
  loading, simResult,
  stepMode, stepStarted, stepDone, schedulerState,
  onRunSingle, onRunAll, onStep, onAutoPlay, autoPlaying,
  stepSpeed, onSpeedChange,
  onReset, onSetStepMode, onViewResults,
  activeTasks, allResults, onNavigateToDashboard,
}) {
  const fullRunDone = !stepMode && allResults && Object.values(allResults).some(Boolean);
  // The protocol whose Gantt/status we display — in step mode it's the step protocol
  const displayProtocol = stepMode ? selectedProtocol : viewProtocol;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>

      {/* ── Controls card ── */}
      <div className="card">
        <p className="card-title">Simulation Controls</p>

        {/* Mode toggle + Speed slider — always visible */}
        <div style={{ display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap", marginBottom: 16 }}>
          <div className="mode-toggle">
            <button
              className={`mode-btn${!stepMode ? " active" : ""}`}
              onClick={() => { if (stepMode) onReset(); }}
            >
              Full Run
            </button>
            <button
              className={`mode-btn${stepMode ? " active" : ""}`}
              onClick={() => { if (!stepMode) onSetStepMode(true); }}
            >
              Step-by-Step
            </button>
          </div>

          {/* Divider */}
          <div style={{ width: 1, height: 24, background: "var(--border)", flexShrink: 0 }} />

          {/* Speed slider — always rendered, only meaningful in step mode */}
          <div style={{ flex: 1, minWidth: 260 }}>
            <SpeedSlider speed={stepSpeed} onChange={onSpeedChange} />
          </div>
        </div>

        {/* Status pills */}
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 14 }}>
          {fullRunDone && !loading && !stepMode && (
            <span style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "#166534", fontWeight: 600, background: "#F0FDF4", border: "1px solid #BBF7D0", borderRadius: 20, padding: "3px 10px" }}>
              ✓ Completed
            </span>
          )}
          {stepMode && stepStarted && !stepDone && (
            <span style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "#4F9CF9", fontWeight: 600, background: "#EFF6FF", border: "1px solid #BFDBFE", borderRadius: 20, padding: "3px 10px" }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#4F9CF9", animation: "spin 1.5s linear infinite", display: "inline-block" }} />
              Stepping — T={schedulerState?.currentTime ?? 0}
            </span>
          )}
        </div>

        {/* ── Full-run controls ── */}
        {!stepMode && (
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>

            {/* Protocol selector */}
            <ProtocolSelector
              selectedProtocol={selectedProtocol}
              onChange={(p) => { onSelectedProtocolChange(p); onViewProtocolChange(p); }}
              allResults={allResults}
              loading={loading}
              disabled={loading}
            />

            {/* Run buttons */}
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
              <button
                className="run-btn"
                onClick={() => onRunSingle(selectedProtocol)}
                disabled={loading}
                style={{ background: PROTO_META[selectedProtocol].color, boxShadow: `0 2px 8px ${PROTO_META[selectedProtocol].color}44` }}
              >
                {loading
                  ? <><span className="spinner" /> Running…</>
                  : <>▶ Run {selectedProtocol === "None" ? "None" : selectedProtocol}</>}
              </button>

              <button
                className="run-btn"
                onClick={onRunAll}
                disabled={loading}
                style={{ background: "var(--surface)", color: "var(--text-sec)", border: "1px solid var(--border)", boxShadow: "none" }}
              >
                {loading ? <><span className="spinner" /> Running…</> : <>⇄ Run All Protocols</>}
              </button>

              {fullRunDone && !loading && (
                <button
                  className="run-btn"
                  onClick={onNavigateToDashboard}
                  style={{ background: "#4CAF50", boxShadow: "0 2px 8px rgba(76,175,80,0.3)" }}
                >
                  📊 View Dashboard
                </button>
              )}
            </div>

            {/* View-protocol switcher — only shown when multiple results exist */}
            {Object.values(allResults).filter(Boolean).length > 1 && (
              <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                <span style={{ fontSize: 11, fontWeight: 600, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.07em" }}>
                  Viewing
                </span>
                {PROTOCOLS.filter(p => allResults[p]).map(p => (
                  <button
                    key={p}
                    onClick={() => onViewProtocolChange(p)}
                    style={{
                      padding: "3px 12px", borderRadius: 20, border: "1px solid",
                      fontSize: 11, fontWeight: 600, cursor: "pointer", transition: "all 0.15s",
                      borderColor: viewProtocol === p ? PROTO_META[p].color : "var(--border)",
                      background:  viewProtocol === p ? PROTO_META[p].color + "18" : "var(--surface)",
                      color:       viewProtocol === p ? PROTO_META[p].color : "var(--text-sec)",
                    }}
                  >
                    {p}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Step-mode controls ── */}
        {stepMode && (
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <ProtocolSelector
              selectedProtocol={selectedProtocol}
              onChange={onSelectedProtocolChange}
              allResults={allResults}
              loading={loading}
              disabled={loading || stepStarted}
            />

            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
              {stepDone ? (
                <button className="run-btn" onClick={onViewResults} style={{ background: "#4CAF50", boxShadow: "0 2px 8px rgba(76,175,80,0.3)" }}>
                  📊 View Results
                </button>
              ) : (
                <>
                  {/* Manual next-step button */}
                  <button
                    className="run-btn"
                    onClick={onStep}
                    disabled={loading || autoPlaying}
                    style={{ background: "var(--accent)", boxShadow: "0 2px 8px rgba(79,156,249,0.35)" }}
                  >
                    {loading && !autoPlaying
                      ? <><span className="spinner" /> Stepping…</>
                      : !stepStarted ? "⏭ Start Stepping"
                      : "⏭ Next Step"}
                  </button>

                  {/* Auto-play / Pause button */}
                  <button
                    className="run-btn"
                    onClick={onAutoPlay}
                    disabled={loading && !autoPlaying}
                    style={{
                      background: autoPlaying ? "#F97316" : "#7C3AED",
                      boxShadow: autoPlaying ? "0 2px 8px rgba(249,115,22,0.35)" : "0 2px 8px rgba(124,58,237,0.35)",
                    }}
                  >
                    {autoPlaying
                      ? <><span className="spinner" style={{ borderTopColor: "#fff" }} /> Pause</>
                      : "▶ Auto Play"}
                  </button>
                </>
              )}

              {stepStarted && (
                <button className="reset-btn" onClick={onReset}>✕ Reset</button>
              )}
            </div>
          </div>
        )}

        {/* Task reference chips */}
        <div style={{ marginTop: 14, display: "flex", gap: 8, flexWrap: "wrap" }}>
          {activeTasks.map(t => (
            <div key={t.name} className="inner-card" style={{ padding: "6px 12px", display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ fontFamily: "Consolas, monospace", fontWeight: 700, fontSize: 13, color: "var(--primary-dk)" }}>{t.name}</span>
              <span style={{ fontSize: 11, color: "var(--text-sec)" }}>P={t.priority}</span>
              {t.needs_resource && <span style={{ fontSize: 10, background: "#EFF6FF", color: "#1D4ED8", borderRadius: 4, padding: "1px 6px", fontWeight: 600 }}>mutex</span>}
            </div>
          ))}
        </div>
      </div>

      {/* ── Scheduler state (step mode) ── */}
      {stepMode && stepStarted && <SchedulerState state={schedulerState} />}

      {/* ── Gantt ── */}
      <GanttSection
        viewProtocol={displayProtocol}
        allResults={allResults}
        simResult={simResult}
        stepMode={stepMode}
        stepStarted={stepStarted}
        stepDone={stepDone}
        stepSpeed={stepSpeed}
      />

    </div>
  );
}
