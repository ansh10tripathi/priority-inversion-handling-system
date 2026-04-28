import { useState } from "react";

const PALETTE = [
  { bg: "#4F9CF9", dim: "#93C5FD", text: "#1D4ED8" },
  { bg: "#6B8F71", dim: "#A8C69F", text: "#1F2A24" },
  { bg: "#F97316", dim: "#FDBA74", text: "#7C2D12" },
  { bg: "#A855F7", dim: "#D8B4FE", text: "#581C87" },
  { bg: "#EF4444", dim: "#FCA5A5", text: "#7F1D1D" },
  { bg: "#EAB308", dim: "#FDE047", text: "#713F12" },
  { bg: "#06B6D4", dim: "#67E8F9", text: "#164E63" },
  { bg: "#84CC16", dim: "#BEF264", text: "#365314" },
];

const CELL_W = 36;
const ROW_H  = 40;

function parseTimeline(timeline) {
  const taskOrder = [];
  const seen = new Set();
  const timeToTask = {};

  timeline.forEach(({ time, task }) => {
    timeToTask[time] = task ?? null;
    if (task && !seen.has(task)) { seen.add(task); taskOrder.push(task); }
  });

  const colorMap = Object.fromEntries(
    taskOrder.map((id, i) => [id, PALETTE[i % PALETTE.length]])
  );
  const maxTime = timeline[timeline.length - 1].time + 1;
  return { taskOrder, colorMap, timeToTask, maxTime };
}

function getLastRunningTime(timeline) {
  for (let i = timeline.length - 1; i >= 0; i--) {
    if (timeline[i].task) return timeline[i].time;
  }
  return -1;
}

function Tooltip({ text, x, y }) {
  if (!text) return null;
  return (
    <div className="gantt-tooltip" style={{ left: x + 14, top: y - 10 }}>
      {text}
    </div>
  );
}

function TimeCell({ time, color, active, isLastRunning, onEnter, onLeave }) {
  const [hovered, setHovered] = useState(false);

  const base = {
    width: CELL_W, height: ROW_H, flexShrink: 0,
    borderRight: "1px solid var(--border)",
    display: "flex", alignItems: "center", justifyContent: "center",
    transition: "background .12s, box-shadow .12s",
    cursor: "default",
  };

  if (!active) {
    return (
      <div
        onMouseEnter={(e) => { setHovered(true);  onEnter(e, time, null); }}
        onMouseLeave={() =>  { setHovered(false); onLeave(); }}
        style={{ ...base, background: hovered ? "#F0F4ED" : "transparent" }}
      >
        <span style={{ fontSize: 9, color: "var(--border2)" }}>—</span>
      </div>
    );
  }

  return (
    <div
      onMouseEnter={(e) => { setHovered(true);  onEnter(e, time, color); }}
      onMouseLeave={() =>  { setHovered(false); onLeave(); }}
      style={{
        ...base,
        background:   isLastRunning ? color.bg : hovered ? color.bg + "55" : color.dim + "88",
        borderTop:    isLastRunning ? `2px solid ${color.bg}` : "2px solid transparent",
        borderBottom: isLastRunning ? `2px solid ${color.bg}` : "2px solid transparent",
        boxShadow:    isLastRunning ? `0 0 10px ${color.bg}44` : "none",
      }}
    >
      <span style={{
        fontSize: 10, fontWeight: 700, fontFamily: "Consolas, monospace",
        color: isLastRunning ? color.text : color.text + "bb",
        userSelect: "none",
      }}>
        {time}
      </span>
    </div>
  );
}

function TaskRow({ id, color, maxTime, timeToTask, lastRunningTime, rowIdx, onEnter, onLeave }) {
  return (
    <div style={{
      display: "flex", alignItems: "stretch",
      background: rowIdx % 2 === 0 ? "#FFFFFF" : "#F8FAF7",
      borderBottom: "1px solid var(--border)",
    }}>
      <div style={{
        width: 48, flexShrink: 0, height: ROW_H,
        display: "flex", alignItems: "center", justifyContent: "flex-end", paddingRight: 10,
      }}>
        <span style={{ fontSize: 12, fontWeight: 700, fontFamily: "Consolas, monospace", color: color.bg }}>
          {id}
        </span>
      </div>
      {Array.from({ length: maxTime }, (_, t) => (
        <TimeCell
          key={t} time={t} color={color}
          active={timeToTask[t] === id}
          isLastRunning={timeToTask[t] === id && t === lastRunningTime}
          onEnter={onEnter} onLeave={onLeave}
        />
      ))}
    </div>
  );
}

function TimeAxis({ maxTime }) {
  return (
    <div style={{ display: "flex", marginLeft: 48 }}>
      {Array.from({ length: maxTime + 1 }, (_, t) => (
        <div key={t} style={{
          width: t < maxTime ? CELL_W : "auto",
          flexShrink: 0,
          borderRight: t < maxTime ? "1px solid var(--border)" : "none",
          borderTop: "1px solid var(--border2)",
          display: "flex", flexDirection: "column", alignItems: "center",
          paddingTop: 4, gap: 2,
        }}>
          <div style={{ width: 1, height: 4, background: "var(--border2)" }} />
          <span style={{ fontSize: 10, color: "var(--text-dim)", fontFamily: "Consolas, monospace" }}>{t}</span>
        </div>
      ))}
    </div>
  );
}

function Legend({ taskOrder, colorMap }) {
  const entries = [
    ...taskOrder.map((id) => ({ label: id, swatch: colorMap[id].bg })),
    { label: "Idle",              swatch: "#F0F4ED", border: "var(--border2)" },
    { label: "Currently running", swatch: "#4F9CF9", glow: true },
  ];
  return (
    <div className="gantt-legend">
      {entries.map(({ label, swatch, border, glow }) => (
        <div key={label} className="legend-item">
          <span className="legend-swatch" style={{
            background: swatch,
            border: border ? `1px solid ${border}` : "none",
            boxShadow: glow ? `0 0 5px ${swatch}66` : "none",
          }} />
          {label}
        </div>
      ))}
    </div>
  );
}

export default function GanttChart({ timeline }) {
  const [tooltip, setTooltip] = useState({ text: null, x: 0, y: 0 });

  if (!timeline?.length) {
    return <p className="empty-state">Run a simulation to see the Gantt chart.</p>;
  }

  const { taskOrder, colorMap, timeToTask, maxTime } = parseTimeline(timeline);
  const lastRunningTime = getLastRunningTime(timeline);

  const showTooltip = (e, time, color) => setTooltip({
    text: color ? `Task ${timeToTask[time]}  ·  T = ${time}` : `Idle  ·  T = ${time}`,
    x: e.clientX, y: e.clientY,
  });
  const hideTooltip = () => setTooltip({ text: null, x: 0, y: 0 });

  return (
    <div style={{ position: "relative" }}>
      <Tooltip text={tooltip.text} x={tooltip.x} y={tooltip.y} />
      <div className="gantt-wrap">
        <div style={{ minWidth: 48 + maxTime * CELL_W }}>
          {taskOrder.map((id, rowIdx) => (
            <TaskRow
              key={id} id={id} color={colorMap[id]}
              maxTime={maxTime} timeToTask={timeToTask}
              lastRunningTime={lastRunningTime} rowIdx={rowIdx}
              onEnter={showTooltip} onLeave={hideTooltip}
            />
          ))}
          <TimeAxis maxTime={maxTime} />
        </div>
      </div>
      <Legend taskOrder={taskOrder} colorMap={colorMap} />
    </div>
  );
}
