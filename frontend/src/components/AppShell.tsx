import { Link, useRouterState, useNavigate } from "@tanstack/react-router";
import {
  LayoutDashboard, Users, Workflow, Brain, FileText,
  LogOut, Activity, Bell, Search,
} from "lucide-react";
import type { ReactNode } from "react";
import { logout, getCurrentUser } from "@/lib/api/auth";

const nav = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/pacientes", label: "Pacientes", icon: Users },
  { to: "/etl", label: "Proceso ETL", icon: Workflow },
  { to: "/ml", label: "Machine Learning", icon: Brain },
  { to: "/reportes", label: "Reportes", icon: FileText },
];

export function AppShell({
  children, title, subtitle,
}: {
  children: ReactNode; title: string; subtitle?: string;
}) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const navigate = useNavigate();
  const user = getCurrentUser();

  async function handleLogout() {
    await logout();
    navigate({ to: "/login" });
  }

  // Iniciales del usuario
  const initials = user?.nombre
    ? user.nombre.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase()
    : "U";

  return (
    <div className="flex min-h-screen bg-background">
      <aside className="w-64 shrink-0 bg-sidebar text-sidebar-foreground flex flex-col">
        <div className="px-6 py-5 border-b border-sidebar-border flex items-center gap-2.5">
          <div className="size-9 rounded-lg bg-primary/20 grid place-items-center ring-1 ring-primary/30">
            <Activity className="size-5 text-primary" />
          </div>
          <div>
            <div className="text-sm font-semibold tracking-tight">HealthAnalytics</div>
            <div className="text-[11px] text-sidebar-foreground/60">Clinical Intelligence</div>
          </div>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {nav.map(({ to, label, icon: Icon }) => {
            const active = to === "/" ? pathname === "/" : pathname.startsWith(to);
            return (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                  active
                    ? "bg-primary/15 text-white ring-1 ring-primary/30"
                    : "text-sidebar-foreground/75 hover:bg-sidebar-accent hover:text-white"
                }`}
              >
                <Icon className="size-4" />
                {label}
              </Link>
            );
          })}
        </nav>
        <div className="p-3 border-t border-sidebar-border">
          <div className="flex items-center gap-3 px-2 py-2">
            <div className="size-9 rounded-full bg-primary/30 grid place-items-center text-sm font-medium text-white">
              {initials}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{user?.nombre ?? "Usuario"}</div>
              <div className="text-[11px] text-sidebar-foreground/60">{user?.rol ?? "—"}</div>
            </div>
            <button
              onClick={handleLogout}
              className="text-sidebar-foreground/60 hover:text-white transition-colors"
              title="Cerrar sesión"
            >
              <LogOut className="size-4" />
            </button>
          </div>
        </div>
      </aside>

      <main className="flex-1 min-w-0">
        <header className="sticky top-0 z-10 border-b border-border bg-background/80 backdrop-blur">
          <div className="flex items-center gap-4 px-8 h-16">
            <div>
              <h1 className="text-lg font-semibold tracking-tight">{title}</h1>
              {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
            </div>
            <div className="ml-auto flex items-center gap-3">
              <div className="relative">
                <Search className="size-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                <input
                  placeholder="Buscar paciente, ID, diagnóstico..."
                  className="h-9 w-80 pl-9 pr-3 rounded-md bg-muted text-sm outline-none focus:ring-2 ring-primary/40"
                />
              </div>
              <button className="size-9 grid place-items-center rounded-md hover:bg-muted relative">
                <Bell className="size-4" />
                <span className="absolute top-2 right-2 size-1.5 rounded-full bg-critical" />
              </button>
            </div>
          </div>
        </header>
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}

export function Card({ children, className = "", onClick }: {
  children: ReactNode; className?: string; onClick?: () => void;
}) {
  return (
    <div
      className={`bg-card rounded-xl border border-border p-5 ${className}`}
      onClick={onClick}
    >
      {children}
    </div>
  );
}

export function RiesgoBadge({ riesgo }: { riesgo: "Bajo" | "Medio" | "Alto" | "Crítico" }) {
  const map = {
    Bajo: "bg-success/15 text-success ring-success/25",
    Medio: "bg-warning/15 text-amber-700 ring-warning/30",
    Alto: "bg-orange-500/15 text-orange-700 ring-orange-500/30",
    Crítico: "bg-critical/15 text-critical ring-critical/30",
  } as const;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-xs font-medium ring-1 ${map[riesgo]}`}>
      <span className="size-1.5 rounded-full bg-current" />
      {riesgo}
    </span>
  );
}
