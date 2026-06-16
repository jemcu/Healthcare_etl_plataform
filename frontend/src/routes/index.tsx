import { createFileRoute } from "@tanstack/react-router";
import { AppShell, Card, RiesgoBadge } from "@/components/AppShell";
import { useQuery } from "@tanstack/react-query";
import { dashboardApi, pacientesApi } from "@/lib/api";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import {
  Bar, BarChart, CartesianGrid, Cell, Line, LineChart,
  Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend,
} from "recharts";
import { AlertTriangle, Droplet, HeartPulse, Activity, Users, TrendingUp, Loader2 } from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({ meta: [{ title: "Dashboard | HealthAnalytics IPS" }] }),
  component: Dashboard,
});

const COLORS = [
  "oklch(0.65 0.16 155)",
  "oklch(0.78 0.16 75)",
  "oklch(0.7 0.18 50)",
  "oklch(0.6 0.22 25)",
];

const tones: Record<string, string> = {
  primary: "text-primary bg-primary/10",
  critical: "text-critical bg-critical/10",
  warning: "text-amber-600 bg-warning/15",
  success: "text-success bg-success/10",
};

function KpiCard({ label, value, sub, icon: Icon, tone = "primary" }: {
  label: string; value: string | number; sub?: string;
  icon: React.ComponentType<{ className: string }>; tone?: keyof typeof tones;
}) {
  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <div className="text-xs text-muted-foreground uppercase tracking-wide">{label}</div>
          <div className="mt-2 text-2xl font-semibold tabular-nums">{value}</div>
          {sub && <div className="text-xs text-muted-foreground mt-1">{sub}</div>}
        </div>
        <div className={`size-10 rounded-lg grid place-items-center ${tones[tone]}`}>
          <Icon className="size-5" />
        </div>
      </div>
    </Card>
  );
}

function Dashboard() {
  useRequireAuth();

  const { data: stats, isLoading: loadingStats } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: () => dashboardApi.getStats(),
  });

  const { data: pacientesData, isLoading: loadingPacientes } = useQuery({
    queryKey: ["pacientes-alertas"],
    queryFn: () => pacientesApi.list(1),
  });

  const isLoading = loadingStats || loadingPacientes;

  if (isLoading) {
    return (
      <AppShell title="Dashboard Clínico" subtitle="Cargando datos...">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="size-8 animate-spin text-primary" />
        </div>
      </AppShell>
    );
  }

  const distribucion = stats?.distribucion_riesgo ?? [];
  const alertas = pacientesData?.results.filter(
    (p) => p.nivel_riesgo === "Crítico" || p.nivel_riesgo === "Alto"
  ).slice(0, 8) ?? [];

  return (
    <AppShell
      title="Dashboard Clínico"
      subtitle="Visión consolidada de la operación de HealthAnalytics IPS"
    >
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          label="Total registros"
          value={(pacientesData?.count ?? 0).toLocaleString()}
          sub="Dataset ETL actual"
          icon={Users}
        />
        <KpiCard
          label="Pacientes críticos"
          value={stats?.pacientes_alto_riesgo ?? 0}
          sub="Requieren intervención"
          icon={AlertTriangle}
          tone="critical"
        />
        <KpiCard
          label="Modelos activos"
          value={stats?.modelos_activos ?? 0}
          sub="ML en producción"
          icon={Activity}
          tone="warning"
        />
        <KpiCard
          label="Precisión promedio"
          value={`${((stats?.precision_promedio ?? 0) * 100).toFixed(1)}%`}
          sub="Validación cruzada k=5"
          icon={TrendingUp}
          tone="success"
        />
      </div>

      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <h3 className="font-semibold mb-1">Distribución de riesgo</h3>
          <p className="text-xs text-muted-foreground mb-3">Clasificación clínica automática</p>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={distribucion}>
              <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.91 0.01 230)" />
              <XAxis dataKey="nivel" stroke="oklch(0.5 0.02 240)" fontSize={12} />
              <YAxis stroke="oklch(0.5 0.02 240)" fontSize={12} />
              <Tooltip contentStyle={{ borderRadius: 8 }} />
              <Bar dataKey="cantidad" fill="oklch(0.55 0.13 200)" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h3 className="font-semibold mb-1">Por nivel de riesgo</h3>
          <p className="text-xs text-muted-foreground mb-3">Clasificación clínica automática</p>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie
                data={distribucion}
                dataKey="cantidad"
                nameKey="nivel"
                innerRadius={55}
                outerRadius={90}
                paddingAngle={2}
              >
                {distribucion.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-1.5 mt-2">
            {distribucion.map((r, i) => (
              <div key={r.nivel} className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-2">
                  <span className="size-2 rounded-sm" style={{ background: COLORS[i % COLORS.length] }} />
                  {r.nivel}
                </span>
                <span className="tabular-nums font-medium">{r.cantidad}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Alertas recientes */}
      {stats?.alertas_recientes && stats.alertas_recientes.length > 0 && (
        <Card className="mt-6">
          <h3 className="font-semibold mb-3">Alertas recientes</h3>
          <div className="space-y-2">
            {stats.alertas_recientes.slice(0, 5).map((a) => (
              <div key={a.id} className="flex items-center gap-3 text-sm py-2 border-b border-border/60 last:border-0">
                <span className="size-2 rounded-full bg-critical shrink-0" />
                <span className="flex-1">{a.mensaje}</span>
                <span className="text-xs text-muted-foreground tabular-nums">{a.fecha}</span>
              </div>
            ))}
          </div>
        </Card>
      )}

      <Card className="mt-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold">Pacientes con alerta clínica</h3>
            <p className="text-xs text-muted-foreground">
              Detectados automáticamente por reglas + modelo predictivo
            </p>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-muted-foreground border-b border-border">
                {["ID", "Paciente", "Edad", "Diagnóstico", "IMC", "Riesgo", "Fecha"].map((h) => (
                  <th key={h} className="py-2 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {alertas.map((p) => (
                <tr key={p.id} className="border-b border-border/60 last:border-0">
                  <td className="py-2.5 font-mono text-xs text-muted-foreground">{p.id}</td>
                  <td className="py-2.5 font-medium">{p.nombre}</td>
                  <td className="py-2.5 tabular-nums">{p.edad}</td>
                  <td className="py-2.5 text-muted-foreground">{p.diagnostico}</td>
                  <td className="py-2.5 tabular-nums">{p.imc}</td>
                  <td className="py-2.5"><RiesgoBadge riesgo={p.nivel_riesgo} /></td>
                  <td className="py-2.5 text-xs text-muted-foreground tabular-nums">{p.fecha_ingreso}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </AppShell>
  );
}
