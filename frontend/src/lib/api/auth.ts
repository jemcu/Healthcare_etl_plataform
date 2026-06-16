import { apiRequest, tokens } from "./client";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface AuthUser {
  id: number;
  email: string;
  nombre: string;
  rol: "Administrador" | "Médico" | "Analista";
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: AuthUser;
}

// ── Login ─────────────────────────────────────────────────────────────────────
export async function login(payload: LoginPayload): Promise<LoginResponse> {
  const data = await apiRequest<LoginResponse>("/api/auth/login/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  tokens.set(data.access, data.refresh);
  localStorage.setItem("user", JSON.stringify(data.user));
  return data;
}

// ── Logout ────────────────────────────────────────────────────────────────────
export async function logout(): Promise<void> {
  const refresh = tokens.refresh;
  if (refresh) {
    await apiRequest("/api/auth/logout/", {
      method: "POST",
      body: JSON.stringify({ refresh }),
    }).catch(() => {});
  }
  tokens.clear();
  localStorage.removeItem("user");
}

// ── Usuario actual ────────────────────────────────────────────────────────────
export function getCurrentUser(): AuthUser | null {
  const raw = localStorage.getItem("user");
  if (!raw) return null;
  try { return JSON.parse(raw) as AuthUser; }
  catch { return null; }
}

export function isAuthenticated(): boolean {
  return !!tokens.access;
}
