const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ── Token helpers ─────────────────────────────────────────────────────────────
export const tokens = {
  get access() { return localStorage.getItem("access_token"); },
  get refresh() { return localStorage.getItem("refresh_token"); },
  set(access: string, refresh: string) {
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
  },
  clear() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  },
};

// ── Refresh silencioso ────────────────────────────────────────────────────────
async function refreshAccessToken(): Promise<string | null> {
  const refresh = tokens.refresh;
  if (!refresh) return null;
  try {
    const res = await fetch(`${API_URL}/api/auth/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) { tokens.clear(); return null; }
    const data = await res.json();
    localStorage.setItem("access_token", data.access);
    return data.access;
  } catch {
    tokens.clear();
    return null;
  }
}

// ── Cliente principal ─────────────────────────────────────────────────────────
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  let token = tokens.access;

  const makeRequest = async (t: string | null) => {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };
    if (t) headers["Authorization"] = `Bearer ${t}`;
    return fetch(`${API_URL}${endpoint}`, { ...options, headers });
  };

  let res = await makeRequest(token);

  // Token expirado → intentar refresh una vez
  if (res.status === 401 && tokens.refresh) {
    token = await refreshAccessToken();
    if (token) {
      res = await makeRequest(token);
    } else {
      // Refresh también falló → redirigir al login
      tokens.clear();
      window.location.href = "/login";
      throw new Error("Sesión expirada");
    }
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Error desconocido" }));
    throw new Error(error.detail || `Error ${res.status}`);
  }

  // 204 No Content
  if (res.status === 204) return {} as T;
  return res.json();
}
