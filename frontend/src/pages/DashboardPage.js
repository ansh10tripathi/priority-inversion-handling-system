// pages/DashboardPage.js
import { useState } from "react";
import ProtocolTabs from "../components/ProtocolTabs";

const PROTOCOLS = ["None", "PIP", "PCP"];

const PROTOCOL_DESC = {
  None: { label: "No Protocol",          desc: "Baseline — priority inversion is not handled. Used for comparison.",          color: "#9CA3AF", icon: "📊" },
  PIP:  { label: "Priority Inheritance", desc: "Reactive: the mutex owner temporarily inherits the highest waiter priority.", color: "#4F9CF9", icon: "⚡" },
  PCP:  { label: "Priority Ceiling",     desc: "Proactive: task priority is raised to the mutex ceiling on acquisition.",     color: "#6B8F71", icon: "🛡" },
};

// ── Sub-components ────────────────────────────────────────────────────────────

function KpiCard({ label, value, sub, accent }) {
  return (
    <div className="card" style={{ padding: "20px 22px" }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>
        {label}
      </div>
      <div style={{ fontSize: 28, fontWeight: 700, color: accent ?? "var(--text)", fontVariantNumeric: "tabular-nums", lineHeight: 1 }}>
        {value}
      </div>
      {sub && <div style={{ fontSize: 11, color: "var(--text-dim)", marginTop: 6 }}>{sub}</div>}
    </div>
  );
}

function ActivityRow({ ev }) {
  const colors = {
    error:     { bg: "#FEF2F2", border: "#E57373", text: "#B91C1C", icon: "✕" },
    inversion: { bg: "#FFF8F0", border: "#F97316", text: "#C2410C", icon: "⚠" },
    protocol:  { bg: "#F0FDF4", border: "#4CAF50", text: "#166534", icon: "⚡" },
    complete:  { bg: "#EFF6FF", border: "#4F9CF9", text: "#1D4ED8", icon: "✓" },
    run:       { bg: "transparent", border: "transparent", text: "var(--text-sec)", icon: "▶" },
    idle:      { bg: "transparent", border: "transparent", text: "var(--text-dim)", icon: "—" },
  };
  const s = colors[ev.type] ?? colors.run;
  return (
    <div style={{
      display: "flex", alignItems: "baseline", gap: 10,
      padding: "5px 10px", borderRadius: 6,
      background: s.bg, borderLeft: `2px solid ${s.border}`,
      fontFamily: "Consolas, monospace", fontSize: 12,
    }}>
      <span style={{ color: "var(--text-dim)", minWidth: 38, flexShrink: 0 }}>T={ev.time}</span>
      <span style={{ color: s.text, flexShrink: 0 }}>{s.icon}</span>
      <span style={{ color: s.text }}>{ev.message}</span>
    </div>
  );
}

// ── Compare view ──────────────────────────────────────────────────────────────

const COMPARE_METRICS = [
  { key: "avg_waiting_time",            label: "Avg Waiting Time",    unit: "tu",    fmt: v => v.toFixed(2), lowerBetter: true  },
  { key: "avg_turnaround_time",         label: "Avg Turnaround Time", unit: "tu",    fmt: v => v.toFixed(2), lowerBetter: true  },
  { key: "priority_inversion_duration", label: "Inversion Duration",  unit: "tu",    fmt: v => v,            lowerBetter: true  },
  { key: "priority_inversion_count",    label: "Inversion Count",     unit: "",      fmt: v => v,            lowerBetter: true  },
  { key: "cpu_utilization",             label: "CPU Utilization",     unit: "%",     fmt: v => v.toFixed(1), lowerBetter: false },
  { key: "context_switches",            label: "Context Switches",    unit: "",      fmt: v => v,            lowerBetter: true  },
  { key: "throughput",                  label: "Throughput",          unit: "t/u",   fmt: v => v.toFixed(3), lowerBetter: false },
];

const PROTO_COLORS = { None: "#9CA3AF", PIP: "#4F9CF9", PCP: "#6B8F71" };

function CompareView({ allResults }) {
  const available = PROTOCOLS.filter(p => !!allResults[p]);
  if (available.length === 0) {
    return <p className="empty-state">Run a simulation to compare protocols.</p>;
  }

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
        <thead>
          <tr style={{ borderBottom: "2px solid var(--border)" }}>
            <th style={{ textAlign: "left", padding: "8px 12px", color: "var(--text-dim)", fontWeight: 600, fontSize: 11, textTransform: "uppercase", letterSpacing: "0.06em" }}>
              Metric
            </th>
            {available.map(p => (
              <th key={p} style={{ textAlign: "right", padding: "8px 12px", color: PROTO_COLORS[p], fontWeight: 700, fontSize: 12 }}>
                {p === "None" ? "None" : p}
              </th>
            ))}
            {available.length > 1 && (
              <th style={{ textAlign: "center", padding: "8px 12px", color: "var(--text-dim)", fontWeight: 600, fontSize: 11, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                Best
              </th>
            )}
          </tr>
        </thead>
        <tbody>
          {COMPARE_METRICS.map(({ key, label, unit, fmt, lowerBetter }, rowIdx) => {
            const values = available.map(p => allResults[p].metrics[key]);
            const best   = lowerBetter ? Math.min(...values) : Math.max(...values);
            return (
              <tr key={key} style={{ borderBottom: "1px solid var(--border)", background: rowIdx % 2 === 0 ? "transparent" : "var(--surface2)" }}>
                <td style={{ padding: "8px 12px", color: "var(--text-sec)" }}>{label}</td>
                {available.map((p, i) => {
                  const v       = values[i];
                  const isBest  = available.length > 1 && v === best;
                  return (
                    <td key={p} style={{
                      padding: "8px 12px", textAlign: "right",
                      fontWeight: isBest ? 700 : 400,
                      fontVariantNumeric: "tabular-nums",
                      color: isBest ? PROTO_COLORS[p] : "var(--text)",
                    }}>
                      {fmt(v)}{unit && <span style={{ fontSize: 10, color: "var(--text-dim)", marginLeft: 3 }}>{unit}</span>}
                    </td>
                  );
                })}
                {available.length > 1 && (
                  <td style={{ padding: "8px 12px", textAlign: "center" }}>
                    {(() => {
                      const bestIdx = values.indexOf(best);
                      const p = available[bestIdx];
                      return (
                        <span style={{
                          fontSize: 10, fontWeight: 700, borderRadius: 10, padding: "2px 8px",
                          background: PROTO_COLORS[p] + "22", color: PROTO_COLORS[p],
                        }}>
                          {p === "None" ? "None" : p}
                        </span>
                      );
                    })()}
                  </td>
                )}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// ── DashboardPage ─────────────────────────────────────────────────────────────

export default function DashboardPage({ allResults, viewProtocol, onViewProtocolChange }) {
  const [showCompare, setShowCompare] = useState(false);

  const result = allResults[viewProtocol];
  const m      = result?.metrics;
  const logs   = result?.logs ?? [];
  const proto  = PROTOCOL_DESC[viewProtocol];

  const anyRun = PROTOCOLS.some(p => !!allResults[p]);

  const kpis = [
    { label: "Total Time",       value: m ? `${m.total_time} u`               : "—", sub: "time units" },
    { label: "Avg Waiting Time", value: m ? m.avg_waiting_time.toFixed(2)      : "—", sub: "time units" },
    { label: "CPU Utilization",  value: m ? `${m.cpu_utilization.toFixed(1)}%` : "—", accent: m ? (m.cpu_utilization >= 80 ? "#4CAF50" : "#F97316") : undefined },
    {
      label: "Inversion Count",
      value: m ? m.priority_inversion_count : "—",
      accent: m ? (m.priority_inversion_count > 0 ? "#E57373" : "#4CAF50") : undefined,
      sub: m?.priority_inversion_count > 0 ? `${m.priority_inversion_duration} tu duration` : (m ? "none detected" : undefined),
    },
  ];

  const notable = logs.filter(e => ["inversion", "protocol", "complete", "error"].includes(e.type)).slice(-8);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>

      {/* ── Protocol tabs + Compare toggle ── */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 12 }}>
        <ProtocolTabs allResults={allResults} viewProtocol={viewProtocol} onChange={onViewProtocolChange} />
        {anyRun && (
          <button
            onClick={() => setShowCompare(v => !v)}
            style={{
              padding: "7px 16px", borderRadius: 8, border: "1px solid var(--border)",
              background: showCompare ? "var(--primary-dk)" : "var(--surface)",
              color: showCompare ? "#fff" : "var(--text-sec)",
              fontSize: 12, fontWeight: 600, cursor: "pointer", transition: "all 0.15s",
            }}
          >
            {showCompare ? "✕ Close Compare" : "⇄ Compare All"}
          </button>
        )}
      </div>

      {/* ── Compare view ── */}
      {showCompare && (
        <div className="card">
          <p className="card-title">Protocol Comparison</p>
          <CompareView allResults={allResults} />
        </div>
      )}

      {/* ── KPI row ── */}
      {!showCompare && (
        <>
          {!m && (
            <div style={{ padding: "16px 20px", borderRadius: 10, background: "var(--surface2)", border: "1px dashed var(--border2)", color: "var(--text-dim)", fontSize: 13, textAlign: "center" }}>
              {anyRun
                ? `No data for ${viewProtocol} — select a completed protocol above.`
                : "Run a simulation to see results."}
            </div>
          )}

          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16 }}>
            {kpis.map(k => <KpiCard key={k.label} {...k} />)}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>

            {/* Protocol info */}
            <div className="card">
              <p className="card-title">Active Protocol</p>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 14 }}>
                <div style={{
                  width: 42, height: 42, borderRadius: 10,
                  background: proto.color + "22", border: `1px solid ${proto.color}44`,
                  display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20,
                }}>
                  {proto.icon}
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 15, color: "var(--text)" }}>{proto.label}</div>
                  <div style={{ fontSize: 11, color: proto.color, fontWeight: 600, marginTop: 1 }}>
                    {viewProtocol === "None" ? "Baseline" : viewProtocol}
                  </div>
                </div>
              </div>
              <p style={{ margin: 0, fontSize: 13, color: "var(--text-sec)", lineHeight: 1.6 }}>{proto.desc}</p>

              {m && (
                <div style={{ marginTop: 16, display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                  {[
                    { label: "Throughput",    value: m.throughput.toFixed(3) + " t/u" },
                    { label: "Avg Response",  value: m.avg_response_time.toFixed(2) + " u" },
                    { label: "Ctx Switches",  value: m.context_switches },
                    { label: "Inv. Duration", value: m.priority_inversion_duration + " u" },
                  ].map(({ label, value }) => (
                    <div key={label} className="inner-card" style={{ padding: "8px 12px" }}>
                      <div className="stat-label">{label}</div>
                      <div style={{ fontSize: 15, fontWeight: 700, color: "var(--text)", fontVariantNumeric: "tabular-nums" }}>{value}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Activity feed */}
            <div className="card">
              <p className="card-title">Recent Activity — {viewProtocol}</p>
              {notable.length === 0
                ? <p className="empty-state" style={{ padding: "20px 0" }}>
                    {m ? "No notable events." : "Run a simulation to see activity."}
                  </p>
                : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                    {notable.map((ev, i) => <ActivityRow key={i} ev={ev} />)}
                  </div>
                )
              }
            </div>

          </div>
        </>
      )}
    </div>
  );
}
