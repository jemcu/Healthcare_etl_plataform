import { createFileRoute } from "@tanstack/react-router";
import { AppShell, Card } from "@/components/AppShell";
import { FileText, FileSpreadsheet, FileType2, Download } from "lucide-react";

export const Route = createFileRoute("/reportes")({
  head: () => ({ meta: [{ title: "Reportes | HealthAnalytics" }] }),
  component: ReportesPage,
});

const reportes = [
  { titulo: "Pacientes críticos del mes", descripcion: "Listado completo con signos vitales y diagnóstico", fecha: "12 jun 2026", tipo: "Clínico" },
  { titulo: "Resumen ejecutivo de KPIs", descripcion: "Indicadores clínicos consolidados para dirección", fecha: "10 jun 2026", tipo: "Gerencial" },
  { titulo: "Resultado entrenamiento ML v3.2", descripcion: "Métricas, matriz de confusión y dataset usado", fecha: "12 jun 2026", tipo: "Analítica" },
  { titulo: "Auditoría ETL · semana 24", descripcion: "Detalle de reglas aplicadas y registros descartados", fecha: "09 jun 2026", tipo: "Auditoría" },
  { titulo: "Segmentación por edad y sexo", descripcion: "Distribución poblacional con métricas de riesgo", fecha: "07 jun 2026", tipo: "Analítica" },
  { titulo: "Alertas tempranas hipertensión", descripcion: "Pacientes con PA sistólica > 140 sostenida", fecha: "05 jun 2026", tipo: "Clínico" },
];

const tipoColor: Record<string, string> = {
  Clínico: "bg-primary/10 text-primary",
  Gerencial: "bg-warning/15 text-amber-700",
  Analítica: "bg-success/10 text-success",
  Auditoría: "bg-muted text-muted-foreground",
};

function ReportesPage() {
  return (
    <AppShell title="Reportes" subtitle="Exporta información clínica en PDF, Excel o CSV">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {[
          { icon: FileType2, label: "Exportar PDF", desc: "Informes formales con branding IPS" },
          { icon: FileSpreadsheet, label: "Exportar Excel", desc: "Datos tabulares con fórmulas" },
          { icon: FileText, label: "Exportar CSV", desc: "Para herramientas externas y BI" },
        ].map(a => (
          <Card key={a.label} className="hover:border-primary/40 transition-colors cursor-pointer">
            <div className="flex items-center gap-3">
              <div className="size-11 rounded-lg bg-primary/10 text-primary grid place-items-center">
                <a.icon className="size-5" />
              </div>
              <div>
                <div className="font-semibold">{a.label}</div>
                <div className="text-xs text-muted-foreground">{a.desc}</div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      <Card>
        <h3 className="font-semibold mb-4">Reportes generados recientemente</h3>
        <div className="divide-y divide-border">
          {reportes.map((r, i) => (
            <div key={i} className="flex items-center gap-4 py-3 first:pt-0 last:pb-0">
              <div className="size-10 rounded-lg bg-muted grid place-items-center text-muted-foreground">
                <FileText className="size-5" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium truncate">{r.titulo}</span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${tipoColor[r.tipo]}`}>{r.tipo}</span>
                </div>
                <div className="text-xs text-muted-foreground mt-0.5">{r.descripcion}</div>
              </div>
              <div className="text-xs text-muted-foreground tabular-nums">{r.fecha}</div>
              <button className="size-9 grid place-items-center rounded-md border border-border hover:bg-muted">
                <Download className="size-4" />
              </button>
            </div>
          ))}
        </div>
      </Card>
    </AppShell>
  );
}
