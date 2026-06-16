import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Activity, ShieldCheck, Loader2 } from "lucide-react";
import { useState } from "react";
import { login } from "../lib/api/auth";

export const Route = createFileRoute("/login")({
  head: () => ({ meta: [{ title: "Iniciar sesión | HealthAnalytics" }] }),
  component: LoginPage,
});

function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("admin@healthanalytics.ips");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login({ email, password });
      navigate({ to: "/" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Credenciales incorrectas");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* Panel izquierdo */}
      <div className="hidden lg:flex bg-sidebar text-sidebar-foreground flex-col justify-between p-12">
        <div className="flex items-center gap-2.5">
          <div className="size-9 rounded-lg bg-primary/20 grid place-items-center ring-1 ring-primary/30">
            <Activity className="size-5 text-primary" />
          </div>
          <span className="font-semibold tracking-tight">HealthAnalytics IPS</span>
        </div>
        <div>
          <h2 className="text-3xl font-semibold tracking-tight max-w-md leading-tight">
            Inteligencia clínica para decisiones que salvan vidas.
          </h2>
          <p className="mt-4 text-sm text-sidebar-foreground/70 max-w-md">
            Plataforma de analítica predictiva, ETL automatizado y dashboards en tiempo real para
            equipos médicos.
          </p>
          <div className="mt-8 flex items-center gap-6 text-xs text-sidebar-foreground/60">
            <span className="flex items-center gap-1.5"><ShieldCheck className="size-4" /> HL7/FHIR</span>
            <span className="flex items-center gap-1.5"><ShieldCheck className="size-4" /> JWT + RBAC</span>
            <span className="flex items-center gap-1.5"><ShieldCheck className="size-4" /> Auditoría completa</span>
          </div>
        </div>
        <div className="text-xs text-sidebar-foreground/40">© 2026 HealthAnalytics IPS</div>
      </div>

      {/* Formulario */}
      <div className="flex items-center justify-center p-8">
        <form className="w-full max-w-sm" onSubmit={handleLogin}>
          <h1 className="text-2xl font-semibold tracking-tight">Iniciar sesión</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Accede al panel clínico con tus credenciales
          </p>

          {error && (
            <div className="mt-4 px-3 py-2 rounded-md bg-destructive/10 border border-destructive/20 text-sm text-destructive">
              {error}
            </div>
          )}

          <div className="mt-8 space-y-4">
            <label className="block">
              <span className="text-xs font-medium text-muted-foreground">Correo institucional</span>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="mt-1 w-full h-10 px-3 rounded-md border border-border bg-background text-sm outline-none focus:ring-2 ring-primary/40"
              />
            </label>
            <label className="block">
              <span className="text-xs font-medium text-muted-foreground">Contraseña</span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="mt-1 w-full h-10 px-3 rounded-md border border-border bg-background text-sm outline-none focus:ring-2 ring-primary/40"
              />
            </label>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-6 w-full h-10 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-60 flex items-center justify-center gap-2"
          >
            {loading && <Loader2 className="size-4 animate-spin" />}
            {loading ? "Entrando..." : "Entrar al dashboard"}
          </button>

          <div className="mt-6 text-xs text-muted-foreground border-t border-border pt-4">
            <div className="font-medium text-foreground mb-1">Roles disponibles</div>
            Administrador · Médico · Analista de datos
          </div>
        </form>
      </div>
    </div>
  );
}
