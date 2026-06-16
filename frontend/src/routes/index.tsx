import { createFileRoute } from "@tanstack/react-router";
import { AppShell, Card, RiesgoBadge } from "@/components/AppShell";
import { kpis, riesgoDistribucion, tendenciaConsultas, diagnosticosCount, pacientes, heatmapCorrelacion } from "@/lib/mockData";
import { Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend } from "recharts";
import { AlertTriangle, Droplet, HeartPulse, Activity, Users, TrendingUp } from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({ meta: [{ title: "Dashboard | HealthAnalytics IPS" }] }),
  component: Dashboard,
});

const COLORS = ["oklch(0.65 0.16 155)", "oklch(0.78 0.16 75)", "oklch(0.7 0.18 50)", "oklch(0.6 0.22 25)"];

function KpiCard({ label, value, sub, icon: Icon, tone = "primary" }: any) {
  const tones: Record<string, string> = {
    primary: "text-primary bg-primary/10",
    critical: "text-critical bg-critical/10",
    warning: "text-amber-600 bg-warning/15",
    success: "text-success bg-success/10",
  };
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
  return (
    <AppShell title="Dashboard Clínico" subtitle="Visión consolidada de la operación de HealthAnalytics IPS">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard label="Total registros" value={kpis.totalRegistros.toLocaleString()} sub="Dataset ETL 12 jun" icon={Users} />
        <KpiCard label="Pacientes críticos" value={kpis.criticos} sub="Requieren intervención" icon={AlertTriangle} tone="critical" />
        <KpiCard label="Hipertensos" value={kpis.hipertensos} sub="PA sistólica > 140" icon={HeartPulse} tone="warning" />
        <KpiCard label="Diabéticos" value={kpis.diabeticos} sub="Glucosa > 140 mg/dL" icon={Droplet} tone="warning" />
      </div>

      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold">Tendencia de consultas</h3>
              <p className="text-xs text-muted-foreground">Consultas vs pacientes críticos detectados</p>
            </div>
            <div className="flex items-center gap-1 text-xs text-success"><TrendingUp className="size-4" /> +12.4%</div>
          </div>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={tendenciaConsultas}>
              <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.91 0.01 230)" />
              <XAxis dataKey="mes" stroke="oklch(0.5 0.02 240)" fontSize={12} />
              <YAxis stroke="oklch(0.5 0.02 240)" fontSize={12} />
              <Tooltip contentStyle={{ borderRadius: 8, border: "1px solid oklch(0.91 0.01 230)" }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Line type="monotone" dataKey="consultas" stroke="oklch(0.55 0.13 200)" strokeWidth={2.5} dot={false} />
              <Line type="monotone" dataKey="criticos" stroke="oklch(0.6 0.22 25)" strokeWidth={2.5} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h3 className="font-semibold mb-1">Distribución de riesgo</h3>
          <p className="text-xs text-muted-foreground mb-3">Clasificación clínica automática</p>
          <ResponsiveContainer width="100%" height={240}>
            <PieChart>
              <Pie data={riesgoDistribucion} dataKey="total" nameKey="riesgo" innerRadius={55} outerRadius={90} paddingAngle={2}>
                {riesgoDistribucion.map((_, i) => <Cell key={i} fill={COLORS[i]} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="space-y-1.5 mt-2">
            {riesgoDistribucion.map((r, i) => (
              <div key={r.riesgo} className="flex items-center justify-between text-xs">
                <span className="flex items-center gap-2"><span className="size-2 rounded-sm" style={{ background: COLORS[i] }} />{r.riesgo}</span>
                <span className="tabular-nums font-medium">{r.total}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-4">
        <Card className="lg:col-span-2">
          <h3 className="font-semibold mb-1">Diagnósticos preliminares</h3>
          <p className="text-xs text-muted-foreground mb-3">Frecuencia post-normalización ETL</p>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={diagnosticosCount}>
              <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.91 0.01 230)" />
              <XAxis dataKey="diagnostico" stroke="oklch(0.5 0.02 240)" fontSize={11} interval={0} angle={-15} textAnchor="end" height={60} />
              <YAxis stroke="oklch(0.5 0.02 240)" fontSize={12} />
              <Tooltip contentStyle={{ borderRadius: 8 }} />
              <Bar dataKey="cantidad" fill="oklch(0.55 0.13 200)" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>

        <Card>
          <h3 className="font-semibold mb-1">Correlación clínica</h3>
          <p className="text-xs text-muted-foreground mb-4">Heatmap de variables predictoras</p>
          <div className="space-y-1.5">
            <div className="grid grid-cols-5 gap-1 text-[10px] text-muted-foreground">
              <div></div>
              {["IMC", "Glucosa", "Presión", "Colest."].map(y => <div key={y} className="text-center">{y}</div>)}
            </div>
            {heatmapCorrelacion.map((row) => (
              <div key={row.x} className="grid grid-cols-5 gap-1 items-center">
                <div className="text-[11px] text-muted-foreground">{row.x}</div>
                {row.values.map((cell) => (
                  <div
                    key={cell.y}
                    className="aspect-square rounded grid place-items-center text-[10px] font-medium text-white tabular-nums"
                    style={{ background: `oklch(${0.85 - cell.v * 0.4} ${0.05 + cell.v * 0.18} 200)` }}
                  >
                    {cell.v.toFixed(2)}
                  </div>
                ))}
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card className="mt-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold">Pacientes con alerta clínica</h3>
            <p className="text-xs text-muted-foreground">Detectados automáticamente por reglas + modelo predictivo</p>
          </div>
          <button className="text-xs text-primary font-medium hover:underline">Ver todos →</button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-muted-foreground border-b border-border">
                <th className="py-2 font-medium">ID</th>
                <th className="py-2 font-medium">Paciente</th>
                <th className="py-2 font-medium">Edad</th>
                <th className="py-2 font-medium">PA</th>
                <th className="py-2 font-medium">Glucosa</th>
                <th className="py-2 font-medium">SatO₂</th>
                <th className="py-2 font-medium">IMC</th>
                <th className="py-2 font-medium">Diagnóstico</th>
                <th className="py-2 font-medium">Riesgo</th>
              </tr>
            </thead>
            <tbody>
              {pacientes.filter(p => p.riesgo === "Crítico" || p.riesgo === "Alto").slice(0, 8).map(p => (
                <tr key={p.id_paciente} className="border-b border-border/60 last:border-0">
                  <td className="py-2.5 font-mono text-xs text-muted-foreground">{p.id_paciente}</td>
                  <td className="py-2.5 font-medium">{p.nombres} {p.apellidos}</td>
                  <td className="py-2.5 tabular-nums">{p.edad}</td>
                  <td className="py-2.5 tabular-nums">{p.presion_sistolica}/{p.presion_diastolica}</td>
                  <td className="py-2.5 tabular-nums">{p.glucosa.toFixed(0)}</td>
                  <td className="py-2.5 tabular-nums">{p.saturacion_oxigeno.toFixed(0)}%</td>
                  <td className="py-2.5 tabular-nums">{p.imc}</td>
                  <td className="py-2.5 text-muted-foreground">{p.diagnostico_preliminar}</td>
                  <td className="py-2.5"><RiesgoBadge riesgo={p.riesgo} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </AppShell>
  );
}
