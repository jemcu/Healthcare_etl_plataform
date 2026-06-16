import { createFileRoute } from "@tanstack/react-router";
import { AppShell, Card } from "@/components/AppShell";
import { etlHistorial } from "@/lib/mockData";
import { CheckCircle2, XCircle, Play, Database, Sparkles, HardDriveDownload, Clock } from "lucide-react";

export const Route = createFileRoute("/etl")({
  head: () => ({ meta: [{ title: "Proceso ETL | HealthAnalytics" }] }),
  component: EtlPage,
});

const pasos = [
  { icon: Database, label: "Extract", descripcion: "Lectura de CSV / API / dataset simulado", duracion: "2.1s", estado: "ok" },
  { icon: Sparkles, label: "Transform", descripcion: "Limpieza, dedup, normalización, IMC, riesgo", duracion: "8.7s", estado: "ok" },
  { icon: HardDriveDownload, label: "Load", descripcion: "Inserción en BD clínica + log histórico", duracion: "1.6s", estado: "ok" },
];

const reglas = [
  { regla: "Eliminar duplicados por id_paciente", afectados: 47 },
  { regla: "Imputación de nulos (mediana en glucosa, peso)", afectados: 132 },
  { regla: "Corrección ortográfica diagnósticos (hipertencion → hipertensión)", afectados: 86 },
  { regla: "Conversión de tipos (edad string → int)", afectados: 24 },
  { regla: "Filtro de valores atípicos (peso > 250, temperatura < 30)", afectados: 9 },
  { regla: "Recálculo IMC = peso / altura²", afectados: 1800 },
  { regla: "Clasificación de riesgo (Bajo / Medio / Alto / Crítico)", afectados: 1800 },
];

function EtlPage() {
  return (
    <AppShell title="Motor ETL" subtitle="Extracción, transformación y carga de datos clínicos">
      <div className="flex items-center justify-between mb-6">
        <div className="text-sm text-muted-foreground">
          Última ejecución: <span className="font-medium text-foreground">2026-06-12 09:32</span> · 1,800 / 1,850 registros válidos
        </div>
        <button className="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90">
          <Play className="size-4" /> Ejecutar ETL ahora
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {pasos.map((p) => (
          <Card key={p.label}>
            <div className="flex items-center gap-3 mb-3">
              <div className="size-10 rounded-lg bg-primary/10 text-primary grid place-items-center">
                <p.icon className="size-5" />
              </div>
              <div>
                <div className="font-semibold">{p.label}</div>
                <div className="text-xs text-muted-foreground">{p.descripcion}</div>
              </div>
            </div>
            <div className="flex items-center justify-between text-xs">
              <span className="flex items-center gap-1 text-success"><CheckCircle2 className="size-3.5" /> Completado</span>
              <span className="flex items-center gap-1 text-muted-foreground tabular-nums"><Clock className="size-3.5" /> {p.duracion}</span>
            </div>
            <div className="mt-3 h-1.5 rounded-full bg-muted overflow-hidden">
              <div className="h-full bg-primary rounded-full" style={{ width: "100%" }} />
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <Card>
          <h3 className="font-semibold mb-1">Reglas aplicadas en última ejecución</h3>
          <p className="text-xs text-muted-foreground mb-4">Transformaciones determinísticas con trazabilidad</p>
          <ul className="space-y-2">
            {reglas.map((r, i) => (
              <li key={i} className="flex items-start justify-between gap-3 text-sm border-b border-border/60 pb-2 last:border-0">
                <span className="text-foreground">{r.regla}</span>
                <span className="shrink-0 px-2 py-0.5 rounded-md bg-primary/10 text-primary text-xs font-medium tabular-nums">{r.afectados}</span>
              </li>
            ))}
          </ul>
        </Card>

        <Card>
          <h3 className="font-semibold mb-1">Logs de ejecución</h3>
          <p className="text-xs text-muted-foreground mb-4">Salida estructurada · stream en tiempo real</p>
          <pre className="bg-sidebar text-sidebar-foreground rounded-lg p-4 text-[11px] font-mono overflow-x-auto leading-relaxed h-64 overflow-y-auto">
{`[09:32:01] INFO  etl.extract  · Cargando dataset_clinico_v3.csv (1,850 filas)
[09:32:03] INFO  etl.extract  · Fuente registrada: file_upload | hash 8f3a..d2
[09:32:03] INFO  etl.transform · Iniciando pipeline de 12 reglas
[09:32:04] WARN  etl.transform · 47 duplicados detectados por id_paciente
[09:32:05] INFO  etl.transform · Imputación mediana aplicada (glucosa: 132 celdas)
[09:32:06] INFO  etl.transform · Normalización diagnósticos: 86 correcciones
[09:32:07] WARN  etl.transform · 9 outliers descartados (peso>250, temp<30)
[09:32:08] INFO  etl.transform · IMC recalculado para 1,800 registros
[09:32:09] INFO  etl.transform · Clasificación de riesgo completada
[09:32:10] INFO  etl.load      · Conectando a clinical_db (postgres://...)
[09:32:11] INFO  etl.load      · Insert masivo: 1,800 filas en pacientes_clean
[09:32:11] INFO  etl.audit     · etl_log #1284 registrado
[09:32:12] DONE  etl           · ✓ Pipeline completado en 12.4s`}
          </pre>
        </Card>
      </div>

      <Card>
        <h3 className="font-semibold mb-4">Histórico de ejecuciones</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-muted-foreground border-b border-border">
              {["#", "Fecha", "Usuario", "Registros", "Válidos", "Duración", "Estado"].map(h => (
                <th key={h} className="py-2 font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {etlHistorial.map(h => (
              <tr key={h.id} className="border-b border-border/60 last:border-0">
                <td className="py-2.5 font-mono text-xs text-muted-foreground">#{h.id}</td>
                <td className="py-2.5 tabular-nums">{h.fecha}</td>
                <td className="py-2.5">{h.usuario}</td>
                <td className="py-2.5 tabular-nums">{h.registros}</td>
                <td className="py-2.5 tabular-nums">{h.validos}</td>
                <td className="py-2.5 tabular-nums">{h.duracion}</td>
                <td className="py-2.5">
                  {h.estado === "Éxito" ? (
                    <span className="inline-flex items-center gap-1 text-xs text-success"><CheckCircle2 className="size-3.5" /> Éxito</span>
                  ) : (
                    <span className="inline-flex items-center gap-1 text-xs text-critical"><XCircle className="size-3.5" /> Error</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </AppShell>
  );
}
