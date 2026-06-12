const API_BASE = import.meta.env.VITE_API_URL || "";

function headers(apiKey) {
  const h = { "Content-Type": "application/json" };
  if (apiKey) h.Authorization = `Bearer ${apiKey}`;
  return h;
}

async function request(path, body, apiKey) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: headers(apiKey),
    body: JSON.stringify(body),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || `Error ${response.status}`);
  }
  return data;
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE}/api/v1/health`);
  return response.json();
}

export const api = {
  architect: (payload, apiKey) => request("/api/v1/architect/analyze", payload, apiKey),
  refactor: (payload, apiKey) => request("/api/v1/refactor/code", payload, apiKey),
  debug: (payload, apiKey) => request("/api/v1/debug/solve", payload, apiKey),
  security: (payload, apiKey) => request("/api/v1/security/audit", payload, apiKey),
  performance: (payload, apiKey) => request("/api/v1/performance/analyze", payload, apiKey),
};
