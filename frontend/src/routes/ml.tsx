import { createFileRoute } from "@tanstack/react-router";
import { AppShell, Card } from "@/components/AppShell";
import { mlMetricas } from "@/lib/mockData";
import { Brain, Zap, Target, TrendingUp } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export const Route = createFileRoute("/ml")({
  head: () => ({ meta: [{ title: "Machine Learning | HealthAnalytics" }] }),
  component: MlPage,
});

const importancia = [
  { feature: "Glucosa", importancia: 0.24 },
  { feature: "Presión sistólica", importancia: 0.21 },
  { feature: "IMC", importancia: 0.17 },
  { feature: "Edad", importancia: 0.14 },
  { feature: "Colesterol", importancia: 0.11 },
  { feature: "Frecuencia cardiaca", importancia: 0.08 },
  { feature: "Fumador", importancia: 0.05 },
];

const clases = ["Bajo", "Medio", "Alto", "Crítico"];

function MlPage() {
  const max = Math.max(...mlMetricas.matriz.flat());
  return (
    <AppShell title="Machine Learning" subtitle="Modelo predictivo de riesgo clínico">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { l: "Accuracy", v: mlMetricas.accuracy, icon: Target },
          { l: "Precision", v: mlMetricas.precision, icon: Zap },
          { l: "Recall", v: mlMetricas.recall, icon: TrendingUp },
          { l: "F1-Score", v: mlMetricas.f1, icon: Brain },
        ].map(m => (
          <Card key={m.l}>
            <div className="flex items-start justify-between">
              <div>
                <div className="text-xs text-muted-foreground uppercase tracking-wide">{m.l}</div>
                <div className="mt-2 text-2xl font-semibold tabular-nums">{(m.v * 100).toFixed(1)}%</div>
                <div className="text-xs text-muted-foreground mt-1">Validación cruzada k=5</div>
              </div>
              <div className="size-10 rounded-lg bg-primary/10 text-primary grid place-items-center">
                <m.icon className="size-5" />
              </div>
            </div>
            <div className="mt-3 h-1.5 rounded-full bg-muted overflow-hidden">
              <div className="h-full bg-primary rounded-full" style={{ width: `${m.v * 100}%` }} />
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <Card>
          <h3 className="font-semibold mb-1">Matriz de confusión</h3>
          <p className="text-xs text-muted-foreground mb-4">Predicción vs real · {mlMetricas.modelo}</p>
          <div className="overflow-x-auto">
            <table className="text-sm">
              <thead>
                <tr>
                  <th className="text-xs text-muted-foreground"></th>
                  <th colSpan={4} className="text-xs text-muted-foreground font-medium pb-2">Predicción</th>
                </tr>
                <tr>
                  <th></th>
                  {clases.map(c => <th key={c} className="text-xs font-medium text-muted-foreground px-3 pb-2">{c}</th>)}
                </tr>
              </thead>
              <tbody>
                {mlMetricas.matriz.map((row, i) => (
                  <tr key={i}>
                    <td className="text-xs text-muted-foreground pr-3 font-medium">{clases[i]}</td>
                    {row.map((v, j) => {
                      const intensity = v / max;
                      const isDiag = i === j;
                      return (
                        <td key={j} className="p-1">
                          <div
                            className="size-16 rounded-md grid place-items-center font-semibold tabular-nums text-sm"
                            style={{
                              background: isDiag
                                ? `oklch(${0.95 - intensity * 0.35} ${0.04 + intensity * 0.14} 200)`
                                : `oklch(${0.97 - intensity * 0.25} ${0.02 + intensity * 0.16} 25)`,
                              color: intensity > 0.5 ? "white" : "var(--foreground)",
                            }}
                          >
                            {v}
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-3 text-xs text-muted-foreground">Filas = clase real · Columnas = predicción del modelo</div>
        </Card>

        <Card>
          <h3 className="font-semibold mb-1">Importancia de variables</h3>
          <p className="text-xs text-muted-foreground mb-4">Coeficientes normalizados del modelo</p>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={importancia} layout="vertical" margin={{ left: 90 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.91 0.01 230)" />
              <XAxis type="number" stroke="oklch(0.5 0.02 240)" fontSize={12} />
              <YAxis type="category" dataKey="feature" stroke="oklch(0.5 0.02 240)" fontSize={12} width={90} />
              <Tooltip contentStyle={{ borderRadius: 8 }} />
              <Bar dataKey="importancia" fill="oklch(0.55 0.13 200)" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      <Card>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold">Predicción individual</h3>
            <p className="text-xs text-muted-foreground">Ingresa variables clínicas y obtén probabilidad de riesgo</p>
          </div>
          <span className="text-xs text-muted-foreground">Modelo: {mlMetricas.modelo} · Entrenado {mlMetricas.entrenado}</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { label: "Edad", placeholder: "62", unit: "años" },
            { label: "IMC", placeholder: "28.4", unit: "kg/m²" },
            { label: "Glucosa", placeholder: "165", unit: "mg/dL" },
            { label: "PA sistólica", placeholder: "148", unit: "mmHg" },
            { label: "Colesterol", placeholder: "230", unit: "mg/dL" },
            { label: "Frec. cardiaca", placeholder: "82", unit: "bpm" },
            { label: "SatO₂", placeholder: "94", unit: "%" },
            { label: "Fumador", placeholder: "Sí / No", unit: "" },
          ].map(f => (
            <label key={f.label} className="block">
              <span className="text-xs text-muted-foreground">{f.label} <span className="text-muted-foreground/60">{f.unit}</span></span>
              <input className="mt-1 w-full h-9 px-3 rounded-md border border-border bg-background text-sm outline-none focus:ring-2 ring-primary/40" placeholder={f.placeholder} />
            </label>
          ))}
        </div>
        <div className="flex items-center gap-3 mt-5">
          <button className="px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90">Ejecutar predicción</button>
          <div className="ml-auto flex items-center gap-2 px-3 py-2 rounded-lg bg-critical/10 ring-1 ring-critical/25">
            <div className="size-2 rounded-full bg-critical animate-pulse" />
            <span className="text-sm font-medium text-critical">Riesgo Alto · 0.78 probabilidad</span>
          </div>
        </div>
      </Card>
    </AppShell>
  );
}
