import { useEffect } from "react";
import { useNavigate } from "@tanstack/react-router";
import { isAuthenticated, getCurrentUser } from "../lib/api/auth";
import type { AuthUser } from "../lib/api/auth";

// Redirige al login si no hay sesión activa
export function useRequireAuth(): AuthUser | null {
  const navigate = useNavigate();
  const user = getCurrentUser();

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate({ to: "/login" });
    }
  }, [navigate]);

  return user;
}
