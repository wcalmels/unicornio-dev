const API_BASE = import.meta.env.VITE_API_URL || "";
const TOKEN_KEY = "unicornio_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function authHeaders() {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

async function parseResponse(response) {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || `Error ${response.status}`);
  }
  return data;
}

export async function register({ email, name, password }) {
  const response = await fetch(`${API_BASE}/api/v1/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, name, password }),
  });
  const data = await parseResponse(response);
  setToken(data.access_token);
  return data;
}

export async function login({ email, password }) {
  const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await parseResponse(response);
  setToken(data.access_token);
  return data;
}

export async function fetchMe() {
  const response = await fetch(`${API_BASE}/api/v1/auth/me`, {
    headers: authHeaders(),
  });
  return parseResponse(response);
}

export async function fetchHistory() {
  const response = await fetch(`${API_BASE}/api/v1/queries/history`, {
    headers: authHeaders(),
  });
  return parseResponse(response);
}

export async function checkHealth() {
  const response = await fetch(`${API_BASE}/api/v1/health`);
  return response.json();
}

async function request(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(body),
  });
  return parseResponse(response);
}

export const api = {
  architect: (payload) => request("/api/v1/architect/analyze", payload),
  refactor: (payload) => request("/api/v1/refactor/code", payload),
  debug: (payload) => request("/api/v1/debug/solve", payload),
  security: (payload) => request("/api/v1/security/audit", payload),
  performance: (payload) => request("/api/v1/performance/analyze", payload),
};
