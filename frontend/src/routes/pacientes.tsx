import { createFileRoute } from "@tanstack/react-router";
import { AppShell, Card, RiesgoBadge } from "@/components/AppShell";
import { useQuery } from "@tanstack/react-query";
import { pacientesApi, reportesApi } from "@/lib/api";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Download, Filter, Loader2 } from "lucide-react";

export const Route = createFileRoute("/pacientes")({
  head: () => ({ meta: [{ title: "Pacientes | HealthAnalytics" }] }),
  component: PacientesPage,
});

const NIVELES = ["Todos", "Bajo", "Medio", "Alto", "Crítico"] as const;

function PacientesPage() {
  useRequireAuth();
  const [filtro, setFiltro] = useState("Todos");
  const [pagina, setPagina] = useState(1);
  const [busqueda, setBusqueda] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["pacientes", pagina, busqueda],
    queryFn: () => pacientesApi.list(pagina, busqueda),
  });

  const pacientes = data?.results ?? [];
  const filtrados = filtro === "Todos"
    ? pacientes
    : pacientes.filter((p) => p.nivel_riesgo === filtro);

  // Distribución por edad para la gráfica
  const edadSegmentacion = [
    { rango: "0-18", pacientes: pacientes.filter((p) => p.edad <= 18).length },
    { rango: "19-35", pacientes: pacientes.filter((p) => p.edad >= 19 && p.edad <= 35).length },
    { rango: "36-50", pacientes: pacientes.filter((p) => p.edad >= 36 && p.edad <= 50).length },
    { rango: "51-65", pacientes: pacientes.filter((p) => p.edad >= 51 && p.edad <= 65).length },
    { rango: "65+", pacientes: pacientes.filter((p) => p.edad > 65).length },
  ];

  return (
    <AppShell
      title="Pacientes"
      subtitle={`${data?.count ?? 0} registros totales`}
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        <Card className="lg:col-span-2">
          <h3 className="font-semibold mb-1">Segmentación por edad</h3>
          <p className="text-xs text-muted-foreground mb-3">Distribución de la población clínica</p>
          {isLoading ? (
            <div className="h-[220px] flex items-center justify-center">
              <Loader2 className="size-6 animate-spin text-primary" />
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={edadSegmentacion}>
                <CartesianGrid strokeDasharray="3 3" stroke="oklch(0.91 0.01 230)" />
                <XAxis dataKey="rango" stroke="oklch(0.5 0.02 240)" fontSize={12} />
                <YAxis stroke="oklch(0.5 0.02 240)" fontSize={12} />
                <Tooltip contentStyle={{ borderRadius: 8 }} />
                <Bar dataKey="pacientes" fill="oklch(0.55 0.13 200)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </Card>
        <Card>
          <h3 className="font-semibold mb-3">Acciones rápidas</h3>
          <div className="space-y-2">
            <button
              onClick={() => reportesApi.generar("excel")}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-md border border-border text-sm font-medium hover:bg-muted"
            >
              <Download className="size-4" /> Exportar Excel
            </button>
            <button
              onClick={() => reportesApi.generar("pdf")}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-md border border-border text-sm font-medium hover:bg-muted"
            >
              <Download className="size-4" /> Exportar PDF
            </button>
            <button
              onClick={() => reportesApi.generar("csv")}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-md border border-border text-sm font-medium hover:bg-muted"
            >
              <Download className="size-4" /> Exportar CSV
            </button>
          </div>
        </Card>
      </div>

      <Card>
        <div className="flex items-center gap-3 mb-4 flex-wrap">
          <Filter className="size-4 text-muted-foreground" />
          {NIVELES.map((f) => (
            <button
              key={f}
              onClick={() => setFiltro(f)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                filtro === f
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-accent"
              }`}
            >
              {f}
            </button>
          ))}
          <input
            value={busqueda}
            onChange={(e) => { setBusqueda(e.target.value); setPagina(1); }}
            placeholder="Buscar paciente..."
            className="ml-auto h-8 px-3 rounded-md border border-border bg-background text-sm outline-none focus:ring-2 ring-primary/40 w-48"
          />
          <span className="text-xs text-muted-foreground tabular-nums">
            {filtrados.length} resultados
          </span>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center h-40">
            <Loader2 className="size-6 animate-spin text-primary" />
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-xs text-muted-foreground border-b border-border">
                    {["ID", "Paciente", "Edad", "Sexo", "IMC", "Diagnóstico", "Riesgo", "Fecha"].map((h) => (
                      <th key={h} className="py-2 font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filtrados.map((p) => (
                    <tr key={p.id} className="border-b border-border/60 last:border-0 hover:bg-muted/30">
                      <td className="py-2.5 font-mono text-xs text-muted-foreground">{p.id}</td>
                      <td className="py-2.5 font-medium">{p.nombre}</td>
                      <td className="py-2.5 tabular-nums">{p.edad}</td>
                      <td className="py-2.5">{p.genero}</td>
                      <td className="py-2.5 tabular-nums">{p.imc}</td>
                      <td className="py-2.5 text-muted-foreground">{p.diagnostico}</td>
                      <td className="py-2.5"><RiesgoBadge riesgo={p.nivel_riesgo} /></td>
                      <td className="py-2.5 text-xs text-muted-foreground tabular-nums">{p.fecha_ingreso}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Paginación */}
            <div className="flex items-center justify-between mt-4 text-xs text-muted-foreground">
              <span>Página {pagina}</span>
              <div className="flex gap-2">
                <button
                  disabled={pagina === 1}
                  onClick={() => setPagina((p) => p - 1)}
                  className="px-3 py-1 rounded-md border border-border hover:bg-muted disabled:opacity-40"
                >
                  ← Anterior
                </button>
                <button
                  disabled={!data || pagina * 20 >= data.count}
                  onClick={() => setPagina((p) => p + 1)}
                  className="px-3 py-1 rounded-md border border-border hover:bg-muted disabled:opacity-40"
                >
                  Siguiente →
                </button>
              </div>
            </div>
          </>
        )}
      </Card>
    </AppShell>
  );
}
