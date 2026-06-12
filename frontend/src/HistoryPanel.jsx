const MODULE_LABELS = {
  architect: "Arquitecto",
  refactor: "Refactor",
  debug: "Debug",
  security: "Seguridad",
  performance: "Performance",
};

export default function HistoryPanel({ items, onSelect, activeId }) {
  if (!items.length) {
    return (
      <div className="history-panel">
        <h3>Historial</h3>
        <p className="history-empty">Aún no hay consultas guardadas.</p>
      </div>
    );
  }

  return (
    <div className="history-panel">
      <h3>Historial</h3>
      <ul className="history-list">
        {items.map((item) => (
          <li key={item.id}>
            <button
              type="button"
              className={activeId === item.id ? "history-item active" : "history-item"}
              onClick={() => onSelect(item)}
            >
              <span className="history-module">
                {MODULE_LABELS[item.module] || item.module}
              </span>
              <span className="history-date">
                {new Date(item.created_at).toLocaleString("es")}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
