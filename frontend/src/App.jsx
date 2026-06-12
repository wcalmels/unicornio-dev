import { useEffect, useState } from "react";
import { api, checkHealth } from "./api";
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
  return Object.fromEntries(
    tab.fields.map((field) => [field.name, field.defaultValue || ""]),
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState(TABS[0]);
  const [form, setForm] = useState(emptyForm(TABS[0]));
  const [apiKey, setApiKey] = useState("");
  const [result, setResult] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);

  useEffect(() => {
    checkHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: "offline" }));
  }, []);

  function selectTab(tab) {
    setActiveTab(tab);
    setForm(emptyForm(tab));
    setResult("");
    setError("");
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult("");

    try {
      const data = await activeTab.action(form, apiKey);
      setResult(data[activeTab.resultKey] || JSON.stringify(data, null, 2));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="hero">
        <div>
          <p className="eyebrow">Unicornio Dev v1.0.0</p>
          <h1>Asistente de desarrollo con IA</h1>
          <p className="subtitle">
            Arquitectura, refactor, debug, seguridad y performance en una sola interfaz.
          </p>
        </div>
        <div className={`status ${health?.status === "healthy" ? "ok" : "warn"}`}>
          API: {health?.status || "conectando..."}
          {health?.claude_configured === false && " · Claude sin configurar"}
        </div>
      </header>

      <main className="layout">
        <aside className="sidebar">
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
        </aside>

        <section className="panel">
          <div className="panel-header">
            <h2>{activeTab.label}</h2>
            <p>{activeTab.description}</p>
          </div>

          <form onSubmit={handleSubmit} className="form">
            <label className="field">
              API Key (opcional)
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Bearer token si está habilitado en el backend"
              />
            </label>

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
