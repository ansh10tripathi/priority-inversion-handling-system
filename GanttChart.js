import { useState } from "react";

// ── Palette ───────────────────────────────────────────────────────────────────

const PALETTE = [
  { bg: "#3b82f6", dim: "#1d4ed8", text: "#eff6ff" }, // blue
  { bg: "#f97316", dim: "#c2410c", text: "#fff7ed" }, // orange
  { bg: "#22c55e", dim: "#15803d", text: "#f0fdf4" }, // green
  { bg: "#eab308", dim: "#a16207", text: "#fefce8" }, // yellow
  { bg: "#a855f7", dim: "#7e22ce", text: "#faf5ff" }, // purple
  { bg: "#ef4444", dim: "#b91c1c", text: "#fef2f2" }, // red
  { bg: "#06b6d4", dim: "#0e7490", text: "#ecfeff" }, // cyan
  { bg: "#84cc16", dim: "#4d7c0f", text: "#f7fee7" }, // lime
];

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Returns { taskOrder, colorMap, runMap, maxTime } derived from timeline */
function parseTimeline(timeline) {
  const taskOrder = [];
  const seen = new Set();
  const runMap = {}; // taskId → { [time]: true }

  timeline.forEach(({ time, task }) => {
    if (task && !seen.has(task)) {
      seen.add(task);
      taskOrder.push(task);
      runMap[task] = {};
    }
    if (task) runMap[task][time] = true;
  });

  const colorMap = Object.fromEntries(
    taskOrder.map((id, i) => [id, PALETTE[i % PALETTE.length]])
  );

  const maxTime = timeline[timeline.length - 1].time + 1;
  return { taskOrder, colorMap, runMap, maxTime };
}

/** Last time unit that has a running task — used for "currently running" highlight */
function getLastRunningTime(timeline) {
  for (let i = timeline.length - 1; i >= 0; i--) {
    if (timeline[i].task) return timeline[i].time;
  }
  return -1;
}

// ── Sub-components ────────────────────────────────────────────────────────────

function Tooltip({ text, x, y }) {
  if (!text) return null;
  return (
    <div
      style={{
        position: "fixed",
        left: x + 12,
        top: y - 8,
        background: "#0f1117",
        border: "1px solid #334155",
        borderRadius: 6,
        padding: "5px 10px",
        fontSize: 11,
        color: "#e2e8f0",
        pointerEvents: "none",
        whiteSpace: "nowrap",
        zIndex: 9999,
        boxShadow: "0 4px 12px rgba(0,0,0,.5)",
      }}
    >
      {text}
    </div>
  );
}

function TaskLabel({ id, color }) {
  return (
    <div
      style={{
        width: 48,
        flexShrink: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "flex-end",
        paddingRight: 10,
        height: 40,
      }}
    >
      <span
        style={{
          fontSize: 12,
          fontWeight: 700,
          fontFamily: "'Consolas', monospace",
          color: color.bg,
        }}
      >
        {id}
      </span>
    </div>
  );
}

function TimeCell({ time, task, color, isRunning, isIdle, onEnter, onLeave }) {
  const [hovered, setHovered] = useState(false);

  const handleEnter = (e) => {
    setHovered(true);
    onEnter(e, time, task);
  };
  const handleLeave = () => {
    setHovered(false);
    onLeave();
  };

  // ── Idle slot ──
  if (isIdle) {
    return (
      <div
        onMouseEnter={handleEnter}
        onMouseLeave={handleLeave}
        style={{
          width: 36,
          height: 40,
          flexShrink: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderRight: "1px solid #1e293b",
          background: hovered ? "#1e293b" : "transparent",
          transition: "background .15s",
          cursor: "default",
        }}
      >
        <span style={{ fontSize: 9, color: "#334155" }}>—</span>
      </div>
    );
  }

  // ── Running slot ──
  const bg = isRunning
    ? color.bg
    : hovered
    ? color.dim
    : color.dim + "cc"; // slightly transparent when not active

  return (
    <div
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
      style={{
        width: 36,
        height: 40,
        flexShrink: 0,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        borderRight: "1px solid #1e293b",
        background: bg,
        borderTop: isRunning ? `2px solid ${color.bg}` : "2px solid transparent",
        borderBottom: isRunning ? `2px solid ${color.bg}` : "2px solid transparent",
        boxShadow: isRunning ? `0 0 8px ${color.bg}55` : "none",
        transition: "background .15s, box-shadow .15s",
        cursor: "default",
        position: "relative",
      }}
    >
      <span
        style={{
          fontSize: 10,
          fontWeight: 700,
          color: isRunning ? color.text : color.text + "99",
          fontFamily: "'Consolas', monospace",
          userSelect: "none",
        }}
      >
        {time}
      </span>
    </div>
  );
}

function TimeAxis({ maxTime }) {
  return (
    <div style={{ display: "flex", marginLeft: 48 }}>
      {Array.from({ length: maxTime }, (_, t) => (
        <div
          key={t}
          style={{
            width: 36,
            flexShrink: 0,
            borderRight: "1px solid #1e293b",
            borderTop: "1px solid #334155",
            paddingTop: 4,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 2,
          }}
        >
          <div style={{ width: 1, height: 4, background: "#475569" }} />
          <span
            style={{
              fontSize: 10,
              color: "#475569",
              fontFamily: "'Consolas', monospace",
            }}
          >
            {t}
          </span>
        </div>
      ))}
      {/* Final tick for maxTime */}
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2, paddingTop: 4 }}>
        <div style={{ width: 1, height: 4, background: "#475569" }} />
        <span style={{ fontSize: 10, color: "#475569", fontFamily: "'Consolas', monospace" }}>
          {maxTime}
        </span>
      </div>
    </div>
  );
}

function Legend({ taskOrder, colorMap }) {
  return (
    <div
      style={{
        display: "flex",
        flexWrap: "wrap",
        gap: "8px 20px",
        marginTop: 16,
        paddingTop: 14,
        borderTop: "1px solid #1e293b",
      }}
    >
      {taskOrder.map((id) => (
        <div key={id} style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <span
            style={{
              width: 10,
              height: 10,
              borderRadius: 2,
              background: colorMap[id].bg,
              display: "inline-block",
              flexShrink: 0,
            }}
          />
          <span style={{ fontSize: 12, color: "#94a3b8" }}>{id}</span>
        </div>
      ))}
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <span
          style={{
            width: 10,
            height: 10,
            borderRadius: 2,
            background: "#1e293b",
            border: "1px solid #334155",
            display: "inline-block",
            flexShrink: 0,
          }}
        />
        <span style={{ fontSize: 12, color: "#475569" }}>Idle</span>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <span
          style={{
            width: 10,
            height: 10,
            borderRadius: 2,
            background: "#3b82f6",
            boxShadow: "0 0 6px #3b82f655",
            display: "inline-block",
            flexShrink: 0,
          }}
        />
        <span style={{ fontSize: 12, color: "#475569" }}>Currently running</span>
      </div>
    </div>
  );
}

// ── GanttChart ────────────────────────────────────────────────────────────────

export default function GanttChart({ timeline }) {
  const [tooltip, setTooltip] = useState({ text: null, x: 0, y: 0 });

  if (!timeline?.length) {
    return (
      <p
        style={{
          textAlign: "center",
          padding: "40px 0",
          color: "#475569",
          fontSize: 14,
          margin: 0,
        }}
      >
        Run a simulation to see the Gantt chart.
      </p>
    );
  }

  const { taskOrder, colorMap, runMap, maxTime } = parseTimeline(timeline);
  const lastRunningTime = getLastRunningTime(timeline);

  // Build a quick lookup: time → task (for idle detection per row)
  const timeToTask = {};
  timeline.forEach(({ time, task }) => { timeToTask[time] = task; });

  const showTooltip = (e, time, task) => {
    setTooltip({
      text: task ? `Task ${task}  ·  T = ${time}` : `Idle  ·  T = ${time}`,
      x: e.clientX,
      y: e.clientY,
    });
  };
  const hideTooltip = () => setTooltip({ text: null, x: 0, y: 0 });

  return (
    <div style={{ position: "relative" }}>
      <Tooltip text={tooltip.text} x={tooltip.x} y={tooltip.y} />

      <div style={{ overflowX: "auto", paddingBottom: 4 }}>
        <div style={{ minWidth: 48 + maxTime * 36 }}>

          {/* ── Task rows ── */}
          {taskOrder.map((id, rowIdx) => {
            const color = colorMap[id];
            return (
              <div
                key={id}
                style={{
                  display: "flex",
                  alignItems: "stretch",
                  background: rowIdx % 2 === 0 ? "#0f1520" : "#0d1219",
                  borderBottom: "1px solid #1e293b",
                }}
              >
                <TaskLabel id={id} color={color} />

                {Array.from({ length: maxTime }, (_, t) => {
                  const taskAtTime = timeToTask[t];
                  const isThisTask = taskAtTime === id;
                  const isIdle = !isThisTask;
                  const isRunning = isThisTask && t === lastRunningTime;

                  return (
                    <TimeCell
                      key={t}
                      time={t}
                      task={isThisTask ? id : null}
                      color={color}
                      isRunning={isRunning}
                      isIdle={isIdle}
                      onEnter={showTooltip}
                      onLeave={hideTooltip}
                    />
                  );
                })}
              </div>
            );
          })}

          {/* ── Time axis ── */}
          <TimeAxis maxTime={maxTime} />
        </div>
      </div>

      {/* ── Legend ── */}
      <Legend taskOrder={taskOrder} colorMap={colorMap} />
    </div>
  );
}
