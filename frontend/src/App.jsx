import { useCallback, useEffect, useState } from "react";
import {
  api,
  checkHealth,
  clearToken,
  fetchHistory,
  fetchMe,
  getToken,
} from "./api";
import AuthScreen from "./AuthScreen";
import HistoryPanel from "./HistoryPanel";
import "./App.css";

const TABS = [
  {
    id: "architect",
    label: "Arquitecto",
    description: "Analiza requisitos y propone arquitectura técnica.",
    fields: [
      { name: "project_name", label: "Nombre del proyecto", type: "text" },
      { name: "description", label: "Descripción", type: "textarea" },
    ],
    action: api.architect,
    resultKey: "analysis",
  },
  {
    id: "refactor",
    label: "Refactor",
    description: "Mejora código siguiendo buenas prácticas.",
    fields: [
      { name: "language", label: "Lenguaje", type: "text", defaultValue: "python" },
      { name: "code", label: "Código", type: "textarea" },
    ],
    action: api.refactor,
    resultKey: "result",
  },
  {
    id: "debug",
    label: "Debug",
    description: "Diagnostica errores y sugiere soluciones.",
    fields: [
      { name: "error", label: "Error", type: "textarea" },
      { name: "context", label: "Contexto", type: "textarea" },
    ],
    action: api.debug,
    resultKey: "solution",
  },
  {
    id: "security",
    label: "Seguridad",
    description: "Audita código en busca de vulnerabilidades.",
    fields: [
      { name: "language", label: "Lenguaje", type: "text", defaultValue: "python" },
      { name: "code", label: "Código", type: "textarea" },
    ],
    action: api.security,
    resultKey: "audit",
  },
  {
    id: "performance",
    label: "Performance",
    description: "Detecta cuellos de botella y optimizaciones.",
    fields: [
      { name: "language", label: "Lenguaje", type: "text", defaultValue: "python" },
      { name: "code", label: "Código", type: "textarea" },
    ],
    action: api.performance,
    resultKey: "analysis",
  },
];

function emptyForm(tab) {
  return Object.fromEntries(tab.fields.map((field) => [field.name, field.defaultValue || ""]));
}

export default function App() {
  const [user, setUser] = useState(null);
  const [booting, setBooting] = useState(true);
  const [activeTab, setActiveTab] = useState(TABS[0]);
  const [form, setForm] = useState(emptyForm(TABS[0]));
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const [history, setHistory] = useState([]);
  const [activeHistoryId, setActiveHistoryId] = useState(null);

  const loadSession = useCallback(async () => {
    if (!getToken()) {
      setUser(null);
      setBooting(false);
      return;
    }
    try {
      const me = await fetchMe();
      setUser(me);
      const items = await fetchHistory();
      setHistory(items);
    } catch {
      clearToken();
      setUser(null);
    } finally {
      setBooting(false);
    }
  }, []);

  useEffect(() => {
    checkHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: "offline" }));
    loadSession();
  }, [loadSession]);

  function selectTab(tab) {
    setActiveTab(tab);
    setForm(emptyForm(tab));
    setResult("");
    setError("");
    setActiveHistoryId(null);
  }

  function handleHistorySelect(item) {
    const tab = TABS.find((t) => t.id === item.module) || TABS[0];
    setActiveTab(tab);
    setForm(item.input_data);
    setResult(item.output_text);
    setError("");
    setActiveHistoryId(item.id);
  }

  function handleLogout() {
    clearToken();
    setUser(null);
    setHistory([]);
    setResult("");
    setError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult("");
    setActiveHistoryId(null);

    try {
      const data = await activeTab.action(form);
      setResult(data[activeTab.resultKey] || JSON.stringify(data, null, 2));
      const items = await fetchHistory();
      setHistory(items);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (booting) {
    return <div className="app loading-screen">Cargando...</div>;
  }

  if (!user) {
    return <AuthScreen onSuccess={loadSession} />;
  }

  return (
    <div className="app">
      <header className="hero">
        <div>
          <p className="eyebrow">Unicornio Dev v1.1.0</p>
          <h1>Hola, {user.name}</h1>
          <p className="subtitle">
            Plan {user.plan} · {user.email}
          </p>
        </div>
        <div className="hero-actions">
          <div className={`status ${health?.status === "healthy" ? "ok" : "warn"}`}>
            API: {health?.status || "conectando..."}
            {health?.claude_configured === false && " · Claude sin configurar"}
          </div>
          <button type="button" className="ghost-btn" onClick={handleLogout}>
            Salir
          </button>
        </div>
      </header>

      <main className="layout layout-wide">
        <aside className="sidebar">
          <div className="sidebar-section">
            <p className="sidebar-label">Herramientas</p>
            {TABS.map((tab) => (
              <button
                key={tab.id}
                className={tab.id === activeTab.id ? "tab active" : "tab"}
                onClick={() => selectTab(tab)}
                type="button"
              >
                {tab.label}
              </button>
            ))}
          </div>
          <HistoryPanel
            items={history}
            onSelect={handleHistorySelect}
            activeId={activeHistoryId}
          />
        </aside>

        <section className="panel">
          <div className="panel-header">
            <h2>{activeTab.label}</h2>
            <p>{activeTab.description}</p>
          </div>

          <form onSubmit={handleSubmit} className="form">
            {activeTab.fields.map((field) => (
              <label key={field.name} className="field">
                {field.label}
                {field.type === "textarea" ? (
                  <textarea
                    rows={8}
                    value={form[field.name]}
                    onChange={(e) =>
                      setForm((prev) => ({ ...prev, [field.name]: e.target.value }))
                    }
                    required={field.name !== "context"}
                  />
                ) : (
                  <input
                    type="text"
                    value={form[field.name]}
                    onChange={(e) =>
                      setForm((prev) => ({ ...prev, [field.name]: e.target.value }))
                    }
                    required
                  />
                )}
              </label>
            ))}

            <button type="submit" disabled={loading}>
              {loading ? "Procesando..." : "Ejecutar"}
            </button>
          </form>

          {error && <pre className="output error">{error}</pre>}
          {result && <pre className="output">{result}</pre>}
        </section>
      </main>
    </div>
  );
}
