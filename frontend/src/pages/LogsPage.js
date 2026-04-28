// pages/LogsPage.js
import { useState, useRef, useEffect } from "react";
import ProtocolTabs from "../components/ProtocolTabs";

const TYPE_ICON  = { error: "✕", inversion: "⚠", protocol: "⚡", complete: "✓", run: "▶", idle: "—" };
const TYPE_LABEL = { error: "Error", inversion: "Inversion", protocol: "Protocol", complete: "Complete", run: "Run", idle: "Idle" };
const FILTERS    = ["all", "inversion", "protocol", "complete", "error", "run"];

export default function LogsPage({ allResults, viewProtocol, onViewProtocolChange }) {
  const [filter, setFilter] = useState("all");
  const bottomRef = useRef(null);

  const logs     = allResults[viewProtocol]?.logs ?? [];
  const filtered = filter === "all" ? logs : logs.filter(e => e.type === filter);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [filtered.length]);

  // Reset filter when switching protocols
  useEffect(() => { setFilter("all"); }, [viewProtocol]);

  const countOf = (type) => type === "all" ? logs.length : logs.filter(e => e.type === type).length;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

      {/* Protocol tabs */}
      <ProtocolTabs allResults={allResults} viewProtocol={viewProtocol} onChange={onViewProtocolChange} />

      {/* Header row */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 15, fontWeight: 700, color: "var(--text)" }}>
            Event Log — {viewProtocol}
          </h2>
          <p style={{ margin: "2px 0 0", fontSize: 12, color: "var(--text-sec)" }}>
            {logs.length} total events · {filtered.length} shown
          </p>
        </div>

        {/* Filter tabs */}
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {FILTERS.map(f => {
            const count  = countOf(f);
            const active = filter === f;
            return (
              <button
                key={f}
                onClick={() => setFilter(f)}
                style={{
                  padding: "4px 12px", borderRadius: 20, border: "1px solid",
                  fontSize: 11, fontWeight: 600, cursor: "pointer", transition: "all 0.15s",
                  borderColor: active ? "var(--primary-dk)" : "var(--border)",
                  background:  active ? "var(--primary-dk)" : "var(--surface)",
                  color:       active ? "#fff" : "var(--text-sec)",
                }}
              >
                {f === "all" ? "All" : TYPE_LABEL[f]}
                {count > 0 && (
                  <span style={{
                    marginLeft: 5, fontSize: 10,
                    background: active ? "rgba(255,255,255,0.25)" : "var(--surface2)",
                    color: active ? "#fff" : "var(--text-dim)",
                    borderRadius: 10, padding: "0 5px",
                  }}>{count}</span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Log panel */}
      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        {filtered.length === 0 ? (
          <p className="empty-state" style={{ padding: "40px 0" }}>
            {logs.length === 0
              ? (allResults[viewProtocol] ? "No events recorded." : "Run a simulation to see logs.")
              : "No events match this filter."}
          </p>
        ) : (
          <div style={{ maxHeight: "calc(100vh - 320px)", overflowY: "auto", display: "flex", flexDirection: "column", scrollbarWidth: "thin", scrollbarColor: "var(--border2) transparent" }}>
            {/* Column header */}
            <div style={{ display: "grid", gridTemplateColumns: "52px 28px 80px 1fr", padding: "8px 16px", borderBottom: "1px solid var(--border)", background: "var(--surface2)", position: "sticky", top: 0, zIndex: 1 }}>
              {["Time", "", "Type", "Message"].map(h => (
                <span key={h} style={{ fontSize: 10, fontWeight: 700, color: "var(--text-dim)", textTransform: "uppercase", letterSpacing: "0.07em" }}>{h}</span>
              ))}
            </div>

            {filtered.map((ev, i) => {
              const colors = {
                error:     { bg: i % 2 === 0 ? "#FEF2F2" : "#FEE2E2", border: "#E57373", text: "#B91C1C" },
                inversion: { bg: i % 2 === 0 ? "#FFF8F0" : "#FFEDD5", border: "#F97316", text: "#C2410C" },
                protocol:  { bg: i % 2 === 0 ? "#F0FDF4" : "#DCFCE7", border: "#4CAF50", text: "#166534" },
                complete:  { bg: i % 2 === 0 ? "#EFF6FF" : "#DBEAFE", border: "#4F9CF9", text: "#1D4ED8" },
                run:       { bg: i % 2 === 0 ? "transparent" : "var(--surface2)", border: "transparent", text: "var(--text)" },
                idle:      { bg: i % 2 === 0 ? "transparent" : "var(--surface2)", border: "transparent", text: "var(--text-dim)" },
              };
              const s = colors[ev.type] ?? colors.run;
              return (
                <div
                  key={i}
                  style={{ display: "grid", gridTemplateColumns: "52px 28px 80px 1fr", padding: "7px 16px", borderLeft: `3px solid ${s.border}`, background: s.bg, alignItems: "center", borderBottom: "1px solid var(--border)" }}
                >
                  <span style={{ fontFamily: "Consolas, monospace", fontSize: 12, color: "var(--text-dim)", fontVariantNumeric: "tabular-nums" }}>{ev.time}</span>
                  <span style={{ fontSize: 13, color: s.text }}>{TYPE_ICON[ev.type] ?? "·"}</span>
                  <span style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em", color: s.text, background: s.border + "22", borderRadius: 4, padding: "1px 6px", display: "inline-block" }}>
                    {TYPE_LABEL[ev.type] ?? ev.type}
                  </span>
                  <span style={{ fontFamily: "Consolas, monospace", fontSize: 12, color: s.text }}>{ev.message}</span>
                </div>
              );
            })}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

    </div>
  );
}
