import { useRef, useEffect } from "react";

const TYPE_ICON = {
  error:     "✕",
  inversion: "⚠",
  protocol:  "⚡",
  complete:  "✓",
  run:       "▶",
  idle:      "—",
};

export default function EventLog({ logs }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs?.length]);

  if (!logs?.length) {
    return <p className="empty-state">No events yet.</p>;
  }

  return (
    <div className="log-wrap">
      {logs.map((ev, i) => (
        <div key={i} className={`log-row ${ev.type}`}>
          <span className="log-time">T={ev.time}</span>
          <span className={`log-icon ${ev.type}`}>{TYPE_ICON[ev.type] ?? "·"}</span>
          <span className={`log-msg ${ev.type}`}>{ev.message}</span>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
