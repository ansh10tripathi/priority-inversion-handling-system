// pages/TasksPage.js
import { useState } from "react";

const EMPTY_FORM = { name: "", priority: "", arrival: "", execution: "", needs_resource: false };

let _idCounter = 1;
function genId() { return `task-${_idCounter++}`; }

// ── Toast ─────────────────────────────────────────────────────────────────────

function Toast({ message, visible }) {
  return (
    <div style={{
      position: "fixed", bottom: 28, left: "50%",
      transform: `translateX(-50%) translateY(${visible ? 0 : 12}px)`,
      opacity: visible ? 1 : 0,
      transition: "opacity 0.25s ease, transform 0.25s ease",
      pointerEvents: "none", zIndex: 9999,
      background: "#1F2A24", color: "#fff",
      fontSize: 13, fontWeight: 600,
      padding: "10px 20px", borderRadius: 10,
      boxShadow: "0 4px 20px rgba(0,0,0,0.25)",
      display: "flex", alignItems: "center", gap: 8,
      whiteSpace: "nowrap",
    }}>
      <span style={{ fontSize: 15 }}>✅</span>
      {message}
    </div>
  );
}

// ── Small reusable field ──────────────────────────────────────────────────────

function Field({ label, type = "text", value, onChange, placeholder, onKeyDown }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <label style={{
        fontSize: 10, fontWeight: 700, color: "var(--text-dim)",
        textTransform: "uppercase", letterSpacing: "0.07em",
      }}>
        {label}
      </label>
      {type === "checkbox" ? (
        <label style={{ display: "flex", alignItems: "center", gap: 7, cursor: "pointer", paddingTop: 5 }}>
          <input
            type="checkbox" checked={value}
            onChange={e => onChange(e.target.checked)}
            style={{ width: 15, height: 15, accentColor: "var(--primary-dk)", cursor: "pointer" }}
          />
          <span style={{ fontSize: 12, color: "var(--text-sec)" }}>Needs mutex</span>
        </label>
      ) : (
        <input
          type={type} value={value}
          onChange={e => onChange(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={placeholder}
          style={{
            padding: "7px 10px", borderRadius: 8,
            border: "1px solid var(--border2)",
            background: "var(--surface)", color: "var(--text)",
            fontSize: 13, outline: "none", width: "100%", fontFamily: "inherit",
            transition: "border-color 0.15s",
          }}
        />
      )}
    </div>
  );
}

// ── TasksPage ─────────────────────────────────────────────────────────────────

export default function TasksPage({ tasks, onTasksChange, onLoadDemo, isActive }) {
  const [form,         setForm]         = useState(EMPTY_FORM);
  const [formError,    setFormError]    = useState("");
  const [selectedId,   setSelectedId]   = useState(null);
  const [sortByArr,    setSortByArr]    = useState(false);
  const [toastVisible, setToastVisible] = useState(false);

  function set(key) { return val => setForm(f => ({ ...f, [key]: val })); }

  // ── Toast helper ───────────────────────────────────────────────────────────

  function showToast() {
    setToastVisible(true);
    setTimeout(() => setToastVisible(false), 2500);
  }

  // ── Load demo (local wrapper) ──────────────────────────────────────────────

  function handleLoadDemo() {
    onLoadDemo();        // update global customTasks state in App
    setSelectedId(null); // clear row selection
    setFormError("");    // clear any form validation error
    showToast();
  }

  // ── Add ────────────────────────────────────────────────────────────────────

  function handleAdd() {
    const name      = form.name.trim();
    const priority  = parseInt(form.priority);
    const arrival   = parseInt(form.arrival);
    const execution = parseInt(form.execution);

    if (!name)                             return setFormError("Name is required.");
    if (tasks.some(t => t.name === name))  return setFormError(`"${name}" already exists.`);
    if (!priority || priority < 1)         return setFormError("Priority must be ≥ 1.");
    if (isNaN(arrival) || arrival < 0)     return setFormError("Arrival must be ≥ 0.");
    if (!execution || execution < 1)       return setFormError("Execution must be ≥ 1.");

    setFormError("");
    const newTask = { id: genId(), name, priority, arrival, execution, needs_resource: form.needs_resource };
    onTasksChange([...tasks, newTask]);
    setForm(EMPTY_FORM);
  }

  function handleKeyDown(e) { if (e.key === "Enter") handleAdd(); }

  // ── Remove selected ────────────────────────────────────────────────────────

  function handleRemoveSelected() {
    if (!selectedId) return;
    onTasksChange(tasks.filter(t => t.id !== selectedId));
    setSelectedId(null);
  }

  // ── Display list (optionally sorted) ──────────────────────────────────────

  const displayed = sortByArr
    ? [...tasks].sort((a, b) => a.arrival - b.arrival)
    : tasks;

  // ── Render ─────────────────────────────────────────────────────────────────

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>

      <Toast message="Demo scenario loaded successfully" visible={toastVisible} />

      {/* ── Header ── */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 10 }}>
        <div>
          <div style={{ fontSize: 15, fontWeight: 700, color: "var(--text)" }}>Task Manager</div>
          <div style={{ fontSize: 12, color: "var(--text-sec)", marginTop: 2 }}>
            {isActive
              ? <span style={{ color: "#166534", fontWeight: 600 }}>✓ Custom tasks active — simulation will use these</span>
              : <span style={{ color: "var(--text-dim)" }}>Demo tasks loaded — edit below or add new tasks</span>}
          </div>
        </div>
        <button
          onClick={handleLoadDemo}
          style={{
            padding: "7px 14px", borderRadius: 8,
            border: "1px solid var(--border2)",
            background: "var(--surface)", color: "var(--text-sec)",
            fontSize: 12, fontWeight: 600, cursor: "pointer",
            display: "flex", alignItems: "center", gap: 6,
          }}
        >
          ↺ Load Demo Scenario
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: 16, alignItems: "start" }}>

        {/* ── Add Task Form ── */}
        <div className="card">
          <p className="card-title">➕ Add Task</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 11 }}>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
              <Field label="Name"      value={form.name}      onChange={set("name")}      placeholder="e.g. T1"  onKeyDown={handleKeyDown} />
              <Field label="Priority"  type="number" value={form.priority}  onChange={set("priority")}  placeholder="1–100" onKeyDown={handleKeyDown} />
              <Field label="Arrival"   type="number" value={form.arrival}   onChange={set("arrival")}   placeholder="≥ 0"   onKeyDown={handleKeyDown} />
              <Field label="Execution" type="number" value={form.execution} onChange={set("execution")} placeholder="≥ 1"   onKeyDown={handleKeyDown} />
            </div>

            <Field label="Resource" type="checkbox" value={form.needs_resource} onChange={set("needs_resource")} />

            {formError && (
              <div style={{
                fontSize: 11, color: "#B91C1C",
                background: "#FEF2F2", border: "1px solid #FECACA",
                borderRadius: 6, padding: "6px 10px",
              }}>
                ⚠ {formError}
              </div>
            )}

            <button
              onClick={handleAdd}
              className="run-btn"
              style={{ alignSelf: "flex-start", padding: "8px 20px", marginTop: 2 }}
            >
              + Add Task
            </button>
          </div>

          {/* ── Quick tips ── */}
          <div style={{
            marginTop: 18, padding: "10px 12px",
            background: "var(--surface2)", borderRadius: 8,
            border: "1px solid var(--border)", fontSize: 11,
            color: "var(--text-dim)", lineHeight: 1.7,
          }}>
            <strong style={{ color: "var(--text-sec)" }}>Tips</strong><br />
            • Press <kbd style={{ background: "var(--border)", borderRadius: 3, padding: "0 4px" }}>Enter</kbd> to add quickly<br />
            • Click a row to select it, then remove<br />
            • Names must be unique
          </div>
        </div>

        {/* ── Task Table ── */}
        <div className="card">

          {/* Table header row */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
            <p className="card-title" style={{ margin: 0 }}>
              📋 Task List
              <span style={{ marginLeft: 8, fontWeight: 400, color: "var(--text-dim)", textTransform: "none", letterSpacing: 0 }}>
                ({tasks.length} task{tasks.length !== 1 ? "s" : ""})
              </span>
            </p>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              {/* Sort toggle */}
              <label style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "var(--text-sec)", cursor: "pointer" }}>
                <input
                  type="checkbox" checked={sortByArr}
                  onChange={e => setSortByArr(e.target.checked)}
                  style={{ accentColor: "var(--primary-dk)", cursor: "pointer" }}
                />
                Sort by arrival
              </label>
              {/* Remove selected */}
              <button
                onClick={handleRemoveSelected}
                disabled={!selectedId}
                style={{
                  padding: "5px 12px", borderRadius: 7,
                  border: "1px solid",
                  borderColor: selectedId ? "#FECACA" : "var(--border2)",
                  background: selectedId ? "#FEF2F2" : "var(--surface2)",
                  color: selectedId ? "#B91C1C" : "var(--text-dim)",
                  fontSize: 11, fontWeight: 600,
                  cursor: selectedId ? "pointer" : "not-allowed",
                  transition: "all 0.15s",
                }}
              >
                ✕ Remove Selected
              </button>
            </div>
          </div>

          {/* Empty state */}
          {tasks.length === 0 ? (
            <div style={{
              padding: "36px 0", textAlign: "center",
              color: "var(--text-dim)", fontSize: 13,
              border: "2px dashed var(--border)", borderRadius: 10,
            }}>
              No tasks yet — add one using the form, or load the demo scenario.
            </div>
          ) : (
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr style={{ borderBottom: "2px solid var(--border)" }}>
                    {["ID", "Name", "Priority", "Arrival", "Execution", "Mutex"].map(h => (
                      <th key={h} style={{
                        padding: "6px 12px", textAlign: "left",
                        fontSize: 10, fontWeight: 700, color: "var(--text-dim)",
                        textTransform: "uppercase", letterSpacing: "0.07em",
                        whiteSpace: "nowrap",
                      }}>
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {displayed.map((t, i) => {
                    const isSelected = t.id === selectedId;
                    return (
                      <tr
                        key={t.id}
                        onClick={() => setSelectedId(isSelected ? null : t.id)}
                        style={{
                          borderBottom: "1px solid var(--border)",
                          background: isSelected
                            ? "rgba(79,156,249,0.10)"
                            : i % 2 === 0 ? "transparent" : "var(--surface2)",
                          cursor: "pointer",
                          outline: isSelected ? "2px solid rgba(79,156,249,0.4)" : "none",
                          outlineOffset: -1,
                          transition: "background 0.1s",
                        }}
                      >
                        <td style={{ padding: "9px 12px", color: "var(--text-dim)", fontSize: 11, fontFamily: "Consolas, monospace" }}>
                          {i + 1}
                        </td>
                        <td style={{ padding: "9px 12px", fontFamily: "Consolas, monospace", fontWeight: 700, color: "var(--primary-dk)" }}>
                          {t.name}
                        </td>
                        <td style={{ padding: "9px 12px", fontVariantNumeric: "tabular-nums" }}>
                          <span style={{
                            display: "inline-block", minWidth: 28, textAlign: "center",
                            background: t.priority >= 4 ? "#FEF3C7" : t.priority >= 2 ? "#EFF6FF" : "#F0FDF4",
                            color:      t.priority >= 4 ? "#92400E" : t.priority >= 2 ? "#1D4ED8" : "#166534",
                            borderRadius: 5, padding: "1px 7px", fontWeight: 700, fontSize: 12,
                          }}>
                            {t.priority}
                          </span>
                        </td>
                        <td style={{ padding: "9px 12px", fontVariantNumeric: "tabular-nums" }}>{t.arrival}</td>
                        <td style={{ padding: "9px 12px", fontVariantNumeric: "tabular-nums" }}>{t.execution}</td>
                        <td style={{ padding: "9px 12px" }}>
                          {t.needs_resource
                            ? <span style={{ fontSize: 10, background: "#EFF6FF", color: "#1D4ED8", borderRadius: 4, padding: "2px 8px", fontWeight: 600 }}>mutex</span>
                            : <span style={{ fontSize: 10, color: "var(--text-dim)" }}>—</span>}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {/* Selection hint */}
          {tasks.length > 0 && (
            <div style={{ marginTop: 12, fontSize: 11, color: "var(--text-dim)" }}>
              {selectedId
                ? <span style={{ color: "#1D4ED8" }}>
                    ● Row selected — click "Remove Selected" to delete, or click again to deselect.
                  </span>
                : "Click any row to select it.  Switch to Simulation → Run to use these tasks."}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
