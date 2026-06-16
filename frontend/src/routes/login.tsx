import { createFileRoute, Link } from "@tanstack/react-router";
import { Activity, ShieldCheck } from "lucide-react";

export const Route = createFileRoute("/login")({
  head: () => ({ meta: [{ title: "Iniciar sesión | HealthAnalytics" }] }),
  component: LoginPage,
});

function LoginPage() {
  return (
    <div className="min-h-screen grid lg:grid-cols-2">
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
            Plataforma de analítica predictiva, ETL automatizado y dashboards en tiempo real para equipos médicos.
          </p>
          <div className="mt-8 flex items-center gap-6 text-xs text-sidebar-foreground/60">
            <span className="flex items-center gap-1.5"><ShieldCheck className="size-4" /> HL7/FHIR</span>
            <span className="flex items-center gap-1.5"><ShieldCheck className="size-4" /> JWT + RBAC</span>
            <span className="flex items-center gap-1.5"><ShieldCheck className="size-4" /> Auditoría completa</span>
          </div>
        </div>
        <div className="text-xs text-sidebar-foreground/40">© 2026 HealthAnalytics IPS</div>
      </div>

      <div className="flex items-center justify-center p-8">
        <form className="w-full max-w-sm">
          <h1 className="text-2xl font-semibold tracking-tight">Iniciar sesión</h1>
          <p className="text-sm text-muted-foreground mt-1">Accede al panel clínico con tus credenciales</p>

          <div className="mt-8 space-y-4">
            <label className="block">
              <span className="text-xs font-medium text-muted-foreground">Correo institucional</span>
              <input type="email" defaultValue="admin@healthanalytics.ips" className="mt-1 w-full h-10 px-3 rounded-md border border-border bg-background text-sm outline-none focus:ring-2 ring-primary/40" />
            </label>
            <label className="block">
              <span className="text-xs font-medium text-muted-foreground">Contraseña</span>
              <input type="password" defaultValue="••••••••" className="mt-1 w-full h-10 px-3 rounded-md border border-border bg-background text-sm outline-none focus:ring-2 ring-primary/40" />
            </label>
            <div className="flex items-center justify-between text-xs">
              <label className="flex items-center gap-2 text-muted-foreground">
                <input type="checkbox" className="rounded" defaultChecked /> Recordar sesión
              </label>
              <a className="text-primary font-medium hover:underline" href="#">¿Olvidaste tu contraseña?</a>
            </div>
          </div>

          <Link to="/" className="mt-6 block">
            <button type="button" className="w-full h-10 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90">
              Entrar al dashboard
            </button>
          </Link>

          <div className="mt-6 text-xs text-muted-foreground border-t border-border pt-4">
            <div className="font-medium text-foreground mb-1">Roles disponibles</div>
            Administrador · Médico · Analista de datos
          </div>
        </form>
      </div>
    </div>
  );
}
