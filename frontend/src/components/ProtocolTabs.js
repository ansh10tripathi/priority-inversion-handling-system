// components/ProtocolTabs.js

const PROTOCOLS = ["None", "PIP", "PCP"];

const PROTO_META = {
  None: { label: "None", sub: "Baseline",             color: "#9CA3AF" },
  PIP:  { label: "PIP",  sub: "Priority Inheritance",  color: "#4F9CF9" },
  PCP:  { label: "PCP",  sub: "Priority Ceiling",      color: "#6B8F71" },
};

export default function ProtocolTabs({ allResults, viewProtocol, onChange }) {
  return (
    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
      {PROTOCOLS.map(p => {
        const meta   = PROTO_META[p];
        const done   = !!allResults[p];
        const active = viewProtocol === p;
        return (
          <button
            key={p}
            onClick={() => done && onChange(p)}
            disabled={!done}
            style={{
              display: "flex", flexDirection: "column", alignItems: "flex-start",
              padding: "8px 16px", borderRadius: 10, border: "2px solid",
              cursor: done ? "pointer" : "not-allowed",
              transition: "all 0.15s",
              borderColor: active ? meta.color : done ? meta.color + "55" : "var(--border)",
              background:  active ? meta.color + "18" : "var(--surface)",
              opacity: done ? 1 : 0.5,
              minWidth: 90,
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <span style={{ fontSize: 13, fontWeight: 700, color: active ? meta.color : "var(--text)" }}>
                {meta.label}
              </span>
              <span style={{
                fontSize: 9, fontWeight: 700, borderRadius: 10, padding: "1px 6px",
                background: done ? (active ? meta.color + "33" : "#F0FDF4") : "var(--surface2)",
                color: done ? (active ? meta.color : "#166534") : "var(--text-dim)",
              }}>
                {done ? "✓ Done" : "Not Run"}
              </span>
            </div>
            <span style={{ fontSize: 10, color: "var(--text-dim)", marginTop: 2 }}>{meta.sub}</span>
          </button>
        );
      })}
    </div>
  );
}
