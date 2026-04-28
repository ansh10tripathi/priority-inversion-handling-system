// pages/MetricsPage.js
import { useState } from "react";
import MetricsPanel from "../MetricsPanel";
import ProtocolTabs from "../components/ProtocolTabs";

const API = "http://127.0.0.1:8000";

const METRIC_EXPLAINERS = [
  { key: "avg_waiting_time",            label: "Avg Waiting Time",    desc: "Average time tasks spend waiting in the ready queue before getting CPU." },
  { key: "avg_turnaround_time",         label: "Avg Turnaround Time", desc: "Average time from task arrival to completion." },
  { key: "priority_inversion_duration", label: "Inversion Duration",  desc: "Total time units during which a priority inversion was active." },
];

const GANTT_IMAGES = [
  { file: "gantt_none.png", label: "None Protocol", accent: "#9CA3AF" },
  { file: "gantt_pip.png",  label: "PIP Protocol",  accent: "#4F9CF9" },
  { file: "gantt_pcp.png",  label: "PCP Protocol",  accent: "#6B8F71" },
];

const COMPARISON_IMAGES = [
  { file: "comparison_waiting_time.png",      label: "Avg Waiting Time" },
  { file: "comparison_turnaround_time.png",   label: "Avg Turnaround Time" },
  { file: "comparison_inversion_duration.png",label: "Inversion Duration" },
  { file: "comparison_context_switches.png",  label: "Context Switches" },
];

function SimGraph({ file, label, accent, graphsKey }) {
  const [status, setStatus] = useState("loading");
  const src = `${API}/output/${file}${graphsKey ? `?v=${graphsKey}` : ""}`;

  return (
    <div className="card" style={{ padding: 0, overflow: "hidden" }}>
      <div style={{ padding: "10px 16px", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", gap: 8 }}>
        {accent && <span style={{ width: 10, height: 10, borderRadius: "50%", background: accent, flexShrink: 0 }} />}
        <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-sec)", textTransform: "uppercase", letterSpacing: "0.07em" }}>
          {label}
        </span>
      </div>
      <div style={{ position: "relative", background: "var(--surface2)", minHeight: 180 }}>
        {status === "loading" && (
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 8 }}>
            <span className="spinner" style={{ width: 20, height: 20, borderWidth: 3, borderColor: "var(--border2)", borderTopColor: "var(--primary-dk)" }} />
            <span style={{ fontSize: 11, color: "var(--text-dim)" }}>Loading…</span>
          </div>
        )}
        {status === "error" && (
          <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", flexDirection: "column", gap: 6 }}>
            <span style={{ fontSize: 22 }}>📊</span>
            <span style={{ fontSize: 11, color: "var(--text-dim)", textAlign: "center", padding: "0 16px" }}>
              Graph not available yet.<br />Run a simulation to generate it.
            </span>
          </div>
        )}
        <img
          src={src} alt={label}
          onLoad={() => setStatus("ok")}
          onError={() => setStatus("error")}
          style={{ width: "100%", display: "block", opacity: status === "ok" ? 1 : 0, transition: "opacity 0.3s" }}
        />
      </div>
    </div>
  );
}

function ExplainerCard({ label, desc, value }) {
  return (
    <div className="inner-card" style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.07em" }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 700, color: "var(--text)", fontVariantNumeric: "tabular-nums" }}>
        {value != null ? (typeof value === "number" ? value.toFixed(2) : value) : "—"}
        {value != null && <span style={{ fontSize: 11, color: "var(--text-dim)", marginLeft: 4 }}>tu</span>}
      </div>
      <div style={{ fontSize: 11, color: "var(--text-sec)", lineHeight: 1.5 }}>{desc}</div>
    </div>
  );
}

export default function MetricsPage({ allResults, viewProtocol, onViewProtocolChange, graphsKey }) {
  const result = allResults[viewProtocol];
  const m      = result?.metrics;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>

      {/* Protocol tabs */}
      <ProtocolTabs allResults={allResults} viewProtocol={viewProtocol} onChange={onViewProtocolChange} />

      {/* KPI explainers */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 14 }}>
        {METRIC_EXPLAINERS.map(({ key, label, desc }) => (
          <ExplainerCard key={key} label={label} desc={desc} value={m?.[key] ?? null} />
        ))}
      </div>

      {/* Bar charts + stat grid */}
      <div className="card">
        <p className="card-title">Performance Charts — {viewProtocol}</p>
        <MetricsPanel metrics={m} />
      </div>

      {/* Full metrics table */}
      {m && (
        <div className="card">
          <p className="card-title">Full Metrics Table — {viewProtocol}</p>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ borderBottom: "2px solid var(--border)" }}>
                <th style={{ textAlign: "left",  padding: "6px 10px", color: "var(--text-dim)", fontWeight: 600, fontSize: 11, textTransform: "uppercase", letterSpacing: "0.06em" }}>Metric</th>
                <th style={{ textAlign: "right", padding: "6px 10px", color: "var(--text-dim)", fontWeight: 600, fontSize: 11, textTransform: "uppercase", letterSpacing: "0.06em" }}>Value</th>
              </tr>
            </thead>
            <tbody>
              {[
                { label: "Total Time",          value: `${m.total_time} u` },
                { label: "Avg Waiting Time",    value: `${m.avg_waiting_time.toFixed(2)} tu` },
                { label: "Avg Turnaround Time", value: `${m.avg_turnaround_time.toFixed(2)} tu` },
                { label: "Avg Response Time",   value: `${m.avg_response_time.toFixed(2)} tu` },
                { label: "CPU Utilization",     value: `${m.cpu_utilization.toFixed(1)}%` },
                { label: "Context Switches",    value: m.context_switches },
                { label: "Throughput",          value: `${m.throughput.toFixed(4)} tasks/u` },
                { label: "Inversion Count",     value: m.priority_inversion_count, warn: m.priority_inversion_count > 0 },
                { label: "Inversion Duration",  value: `${m.priority_inversion_duration} tu`, warn: m.priority_inversion_duration > 0 },
              ].map(({ label, value, warn }, i) => (
                <tr key={label} style={{ borderBottom: "1px solid var(--border)", background: i % 2 === 0 ? "transparent" : "var(--surface2)" }}>
                  <td style={{ padding: "8px 10px", color: "var(--text-sec)" }}>{label}</td>
                  <td style={{ padding: "8px 10px", textAlign: "right", fontWeight: 600, fontVariantNumeric: "tabular-nums", color: warn ? "#E57373" : "var(--text)" }}>
                    {value}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Gantt Charts */}
      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
          <h2 style={{ margin: 0, fontSize: 13, fontWeight: 700, color: "var(--text)" }}>Gantt Charts</h2>
          <span style={{ fontSize: 11, color: "var(--text-dim)" }}>— one per protocol</span>
          {!graphsKey && (
            <span style={{ fontSize: 10, color: "#92400E", background: "#FEF3C7", border: "1px solid #FCD34D", borderRadius: 20, padding: "2px 8px", fontWeight: 600 }}>
              Run simulation to generate
            </span>
          )}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16 }}>
          {GANTT_IMAGES.map(({ file, label, accent }) => (
            <SimGraph key={file} file={file} label={label} accent={accent} graphsKey={graphsKey} />
          ))}
        </div>
      </div>

      {/* Comparison Graphs */}
      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
          <h2 style={{ margin: 0, fontSize: 13, fontWeight: 700, color: "var(--text)" }}>Protocol Comparison</h2>
          <span style={{ fontSize: 11, color: "var(--text-dim)" }}>— None vs PIP vs PCP</span>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 16 }}>
          {COMPARISON_IMAGES.map(({ file, label }) => (
            <SimGraph key={file} file={file} label={label} graphsKey={graphsKey} />
          ))}
        </div>
      </div>

    </div>
  );
}
