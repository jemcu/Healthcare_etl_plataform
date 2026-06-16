import { createFileRoute } from "@tanstack/react-router";
import { AppShell, Card, RiesgoBadge } from "@/components/AppShell";
import { pacientes, edadSegmentacion } from "@/lib/mockData";
import { useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Download, Upload, Filter } from "lucide-react";

export const Route = createFileRoute("/pacientes")({
  head: () => ({ meta: [{ title: "Pacientes | HealthAnalytics" }] }),
  component: PacientesPage,
});

function PacientesPage() {
  const [filtro, setFiltro] = useState<string>("Todos");
  const filtrados = filtro === "Todos" ? pacientes : pacientes.filter(p => p.riesgo === filtro);

  return (
    <AppShell title="Pacientes" subtitle={`${pacientes.length} registros mostrados de 1,800 totales`}>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <Card className="lg:col-span-2">
          <h3 className="font-semibold mb-1">Segmentación por edad</h3>
          <p className="text-xs text-muted-foreground mb-3">Distribución de la población clínica</p>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={edadSegmentacion}>
              <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.91 0.01 230)" />
              <XAxis dataKey="rango" stroke="oklch(0.5 0.02 240)" fontSize={12} />
              <YAxis stroke="oklch(0.5 0.02 240)" fontSize={12} />
              <Tooltip contentStyle={{ borderRadius: 8 }} />
              <Bar dataKey="pacientes" fill="oklch(0.55 0.13 200)" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
        <Card>
          <h3 className="font-semibold mb-3">Acciones rápidas</h3>
          <div className="space-y-2">
            <button className="w-full flex items-center gap-2 px-3 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90">
              <Upload className="size-4" /> Cargar CSV de pacientes
            </button>
            <button className="w-full flex items-center gap-2 px-3 py-2 rounded-md border border-border text-sm font-medium hover:bg-muted">
              <Download className="size-4" /> Exportar Excel
            </button>
            <button className="w-full flex items-center gap-2 px-3 py-2 rounded-md border border-border text-sm font-medium hover:bg-muted">
              <Download className="size-4" /> Exportar PDF
            </button>
          </div>
          <div className="mt-4 pt-4 border-t border-border text-xs text-muted-foreground">
            Último ETL: <span className="font-medium text-foreground">12 jun, 09:32</span> · 1,800 registros válidos
          </div>
        </Card>
      </div>

      <Card>
        <div className="flex items-center gap-3 mb-4">
          <Filter className="size-4 text-muted-foreground" />
          {(["Todos", "Bajo", "Medio", "Alto", "Crítico"] as const).map(f => (
            <button
              key={f}
              onClick={() => setFiltro(f)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                filtro === f ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:bg-accent"
              }`}
            >
              {f}
            </button>
          ))}
          <span className="ml-auto text-xs text-muted-foreground tabular-nums">{filtrados.length} resultados</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-muted-foreground border-b border-border">
                {["ID", "Paciente", "Edad", "Sexo", "IMC", "PA", "Glucosa", "SatO₂", "Diagnóstico", "Riesgo", "Fecha"].map(h => (
                  <th key={h} className="py-2 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtrados.map(p => (
                <tr key={p.id_paciente} className="border-b border-border/60 last:border-0 hover:bg-muted/30">
                  <td className="py-2.5 font-mono text-xs text-muted-foreground">{p.id_paciente}</td>
                  <td className="py-2.5 font-medium">{p.nombres} {p.apellidos}</td>
                  <td className="py-2.5 tabular-nums">{p.edad}</td>
                  <td className="py-2.5">{p.sexo}</td>
                  <td className="py-2.5 tabular-nums">{p.imc}</td>
                  <td className="py-2.5 tabular-nums">{p.presion_sistolica}/{p.presion_diastolica}</td>
                  <td className="py-2.5 tabular-nums">{p.glucosa.toFixed(0)}</td>
                  <td className="py-2.5 tabular-nums">{p.saturacion_oxigeno.toFixed(0)}%</td>
                  <td className="py-2.5 text-muted-foreground">{p.diagnostico_preliminar}</td>
                  <td className="py-2.5"><RiesgoBadge riesgo={p.riesgo} /></td>
                  <td className="py-2.5 text-xs text-muted-foreground tabular-nums">{p.fecha_consulta}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </AppShell>
  );
}
