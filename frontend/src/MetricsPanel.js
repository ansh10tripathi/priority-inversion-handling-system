import { Chart, BarElement, BarController, CategoryScale, LinearScale, Tooltip, Legend } from "chart.js";
import { Bar } from "react-chartjs-2";

Chart.register(BarElement, BarController, CategoryScale, LinearScale, Tooltip, Legend);

const CHARTS = [
  { key: "waiting",    title: "Avg Waiting",    unit: "tu", color: "#4F9CF9", getValue: (m) => m.avg_waiting_time },
  { key: "turnaround", title: "Avg Turnaround", unit: "tu", color: "#6B8F71", getValue: (m) => m.avg_turnaround_time },
  { key: "inversion",  title: "Inv. Duration",  unit: "tu", color: "#E57373", getValue: (m) => m.priority_inversion_duration },
];

const STAT_GRID = [
  { key: "total_time",               label: "Total Time",   fmt: (v) => `${v} u` },
  { key: "avg_response_time",        label: "Avg Response", fmt: (v) => v.toFixed(2) },
  { key: "cpu_utilization",          label: "CPU Util.",    fmt: (v) => `${v.toFixed(1)}%` },
  { key: "context_switches",         label: "Ctx Switches", fmt: (v) => v },
  { key: "priority_inversion_count", label: "Inv. Count",   fmt: (v) => v, warn: true },
  { key: "throughput",               label: "Throughput",   fmt: (v) => v.toFixed(3) },
];

function makeOptions(unit) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    animation: { duration: 500, easing: "easeOutQuart" },
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#1F2A24",
        borderColor: "#E3E7E0",
        borderWidth: 1,
        titleColor: "#9CA3AF",
        bodyColor: "#F5F7F2",
        padding: 10,
        callbacks: { label: (ctx) => ` ${ctx.parsed.y.toFixed(2)} ${unit}` },
      },
    },
    scales: {
      x: {
        grid: { color: "#E3E7E0" },
        ticks: { color: "#9CA3AF", font: { size: 11 } },
        border: { color: "#E3E7E0" },
      },
      y: {
        beginAtZero: true,
        grid: { color: "#E3E7E0" },
        ticks: { color: "#9CA3AF", font: { size: 11 }, maxTicksLimit: 5 },
        border: { color: "#E3E7E0" },
      },
    },
  };
}

function BarChart({ title, unit, color, value }) {
  const chartData = {
    labels: [title],
    datasets: [{
      data: [value ?? 0],
      backgroundColor: color + "33",
      borderColor: color,
      borderWidth: 2,
      borderRadius: 6,
      borderSkipped: false,
      hoverBackgroundColor: color + "55",
    }],
  };

  return (
    <div className="inner-card" style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <span style={{ fontSize: 10, color: "var(--text-dim)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em" }}>
          {title}
        </span>
        <span style={{ fontSize: 20, fontWeight: 700, color, fontVariantNumeric: "tabular-nums" }}>
          {value != null ? value.toFixed(2) : "—"}
          <span style={{ fontSize: 10, color: "var(--text-dim)", marginLeft: 4 }}>{unit}</span>
        </span>
      </div>
      <div style={{ height: 110, position: "relative" }}>
        <Bar data={chartData} options={makeOptions(unit)} />
      </div>
    </div>
  );
}

function StatCard({ label, value, warn }) {
  const isWarn = warn && typeof value === "number" && value > 0;
  return (
    <div className={`stat-card${isWarn ? " warn" : ""}`}>
      <div className="stat-label">{label}</div>
      <div className={`stat-value${isWarn ? " warn" : ""}`}>{value != null ? value : "—"}</div>
    </div>
  );
}

export default function MetricsPanel({ metrics }) {
  if (!metrics) return <p className="empty-state">No metrics yet.</p>;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 10 }}>
        {CHARTS.map(({ key, title, unit, color, getValue }) => (
          <BarChart key={key} title={title} unit={unit} color={color} value={getValue(metrics)} />
        ))}
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 8 }}>
        {STAT_GRID.map(({ key, label, fmt, warn }) => (
          <StatCard key={key} label={label} warn={warn}
            value={metrics[key] != null ? fmt(metrics[key]) : null} />
        ))}
      </div>
    </div>
  );
}
