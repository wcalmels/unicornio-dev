export function getWebviewHtml(): string {
  return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline';" />
  <style>
    :root {
      color-scheme: light dark;
      font-family: var(--vscode-font-family);
      font-size: var(--vscode-font-size);
      color: var(--vscode-foreground);
      background: var(--vscode-sideBar-background);
    }
    body { margin: 0; padding: 12px; }
    h1, h2, h3, p { margin: 0 0 8px; }
    .muted { color: var(--vscode-descriptionForeground); font-size: 12px; }
    .card {
      border: 1px solid var(--vscode-widget-border);
      border-radius: 8px;
      padding: 12px;
      margin-bottom: 12px;
      background: var(--vscode-editor-background);
    }
    label { display: block; margin-bottom: 10px; font-size: 12px; }
    input, textarea, select, button {
      width: 100%;
      box-sizing: border-box;
      margin-top: 4px;
      border-radius: 6px;
      border: 1px solid var(--vscode-input-border);
      background: var(--vscode-input-background);
      color: var(--vscode-input-foreground);
      padding: 8px;
      font: inherit;
    }
    button {
      cursor: pointer;
      background: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
      border: none;
      margin-top: 8px;
    }
    button.secondary {
      background: var(--vscode-button-secondaryBackground);
      color: var(--vscode-button-secondaryForeground);
    }
    .tabs { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
    .tab {
      flex: 1;
      min-width: 70px;
      padding: 6px 8px;
      border-radius: 6px;
      border: 1px solid var(--vscode-widget-border);
      background: transparent;
      color: inherit;
      cursor: pointer;
    }
    .tab.active {
      background: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
      border-color: transparent;
    }
    #result {
      white-space: pre-wrap;
      font-family: var(--vscode-editor-font-family);
      font-size: 12px;
      min-height: 120px;
      max-height: 280px;
      overflow: auto;
      border: 1px solid var(--vscode-widget-border);
      border-radius: 6px;
      padding: 8px;
      background: var(--vscode-textCodeBlock-background);
    }
    .history-item {
      padding: 8px;
      border-bottom: 1px solid var(--vscode-widget-border);
      cursor: pointer;
      font-size: 12px;
    }
    .hidden { display: none; }
    .error { color: var(--vscode-errorForeground); }
  </style>
</head>
<body>
  <div id="authView" class="card">
    <h2>Unicornio Dev</h2>
    <p class="muted">Inicia sesión para usar el asistente de IA.</p>
    <label>Email<input id="email" type="email" /></label>
    <label>Contraseña<input id="password" type="password" /></label>
    <label>Nombre (solo registro)<input id="name" type="text" /></label>
    <button id="loginBtn">Iniciar sesión</button>
    <button id="registerBtn" class="secondary">Crear cuenta</button>
    <p id="authError" class="error hidden"></p>
  </div>

  <div id="appView" class="hidden">
    <div class="card">
      <h3 id="userTitle">Hola</h3>
      <p class="muted" id="userMeta"></p>
      <button id="logoutBtn" class="secondary">Cerrar sesión</button>
    </div>

    <div class="tabs" id="tabs"></div>

    <div class="card">
      <div id="fields"></div>
      <button id="runBtn">Ejecutar</button>
      <p id="runError" class="error hidden"></p>
    </div>

    <div class="card">
      <h3>Resultado</h3>
      <div id="result">Sin resultados aún.</div>
    </div>

    <div class="card">
      <h3>Historial</h3>
      <div id="history"></div>
    </div>
  </div>

  <script>
    const vscode = acquireVsCodeApi();

    const TABS = [
      { id: "architect", label: "Arquitecto", fields: [
        { name: "project_name", label: "Proyecto", type: "text" },
        { name: "description", label: "Descripción", type: "textarea" },
      ]},
      { id: "refactor", label: "Refactor", fields: [
        { name: "hint", label: "Usa la selección del editor o el archivo activo", type: "note" },
      ]},
      { id: "debug", label: "Debug", fields: [
        { name: "error", label: "Error", type: "textarea" },
        { name: "context", label: "Contexto", type: "textarea" },
      ]},
      { id: "security", label: "Seguridad", fields: [
        { name: "hint", label: "Analiza el archivo activo", type: "note" },
      ]},
      { id: "performance", label: "Performance", fields: [
        { name: "hint", label: "Analiza el archivo activo", type: "note" },
      ]},
    ];

    let activeTab = TABS[0];
    let form = {};

    function post(type, payload = {}) {
      vscode.postMessage({ type, ...payload });
    }

    function showAuth() {
      document.getElementById("authView").classList.remove("hidden");
      document.getElementById("appView").classList.add("hidden");
    }

    function showApp(user) {
      document.getElementById("authView").classList.add("hidden");
      document.getElementById("appView").classList.remove("hidden");
      document.getElementById("userTitle").textContent = "Hola, " + user.name;
      document.getElementById("userMeta").textContent = user.email + " · plan " + user.plan;
      renderTabs();
      renderFields();
      post("loadHistory");
    }

    function renderTabs() {
      const container = document.getElementById("tabs");
      container.innerHTML = "";
      TABS.forEach((tab) => {
        const btn = document.createElement("button");
        btn.className = "tab" + (tab.id === activeTab.id ? " active" : "");
        btn.textContent = tab.label;
        btn.onclick = () => {
          activeTab = tab;
          form = {};
          renderTabs();
          renderFields();
        };
        container.appendChild(btn);
      });
    }

    function renderFields() {
      const container = document.getElementById("fields");
      container.innerHTML = "";
      activeTab.fields.forEach((field) => {
        if (field.type === "note") {
          const p = document.createElement("p");
          p.className = "muted";
          p.textContent = field.label;
          container.appendChild(p);
          return;
        }
        const label = document.createElement("label");
        label.textContent = field.label;
        const input = field.type === "textarea"
          ? document.createElement("textarea")
          : document.createElement("input");
        input.rows = 4;
        input.value = form[field.name] || "";
        input.oninput = (e) => { form[field.name] = e.target.value; };
        label.appendChild(input);
        container.appendChild(label);
      });
    }

    function renderHistory(items) {
      const container = document.getElementById("history");
      container.innerHTML = "";
      if (!items.length) {
        container.innerHTML = '<p class="muted">Sin consultas.</p>';
        return;
      }
      items.forEach((item) => {
        const div = document.createElement("div");
        div.className = "history-item";
        div.textContent = item.module + " · " + (item.created_at || "").slice(0, 19);
        div.onclick = () => {
          document.getElementById("result").textContent = item.output_text || "";
        };
        container.appendChild(div);
      });
    }

    document.getElementById("loginBtn").onclick = () => {
      post("login", {
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
      });
    };

    document.getElementById("registerBtn").onclick = () => {
      post("register", {
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
        name: document.getElementById("name").value,
      });
    };

    document.getElementById("logoutBtn").onclick = () => post("logout");
    document.getElementById("runBtn").onclick = () => post("run", { module: activeTab.id, form });

    window.addEventListener("message", (event) => {
      const msg = event.data;
      if (msg.type === "authRequired") showAuth();
      if (msg.type === "authError") {
        const el = document.getElementById("authError");
        el.textContent = msg.message;
        el.classList.remove("hidden");
      }
      if (msg.type === "authenticated") showApp(msg.user);
      if (msg.type === "runError") {
        const el = document.getElementById("runError");
        el.textContent = msg.message;
        el.classList.remove("hidden");
      }
      if (msg.type === "runStart") {
        document.getElementById("runError").classList.add("hidden");
        document.getElementById("result").textContent = "Procesando...";
      }
      if (msg.type === "runChunk") {
        const el = document.getElementById("result");
        if (el.textContent === "Procesando...") el.textContent = "";
        el.textContent += msg.text;
      }
      if (msg.type === "runComplete") {
        document.getElementById("result").textContent = msg.result;
        post("loadHistory");
      }
      if (msg.type === "history") renderHistory(msg.items || []);
    });

    post("ready");
  </script>
</body>
</html>`;
}
