import { createFileRoute } from "@tanstack/react-router";
import { AppShell, Card } from "@/components/AppShell";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { etlApi } from "@/lib/api";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import {
  CheckCircle2, XCircle, Play, Database, Sparkles,
  HardDriveDownload, Clock, Loader2,
} from "lucide-react";

export const Route = createFileRoute("/etl")({
  head: () => ({ meta: [{ title: "Proceso ETL | HealthAnalytics" }] }),
  component: EtlPage,
});

const pasos = [
  { icon: Database, label: "Extract", descripcion: "Lectura del dataset clínico" },
  { icon: Sparkles, label: "Transform", descripcion: "Limpieza, dedup, normalización, IMC, riesgo" },
  { icon: HardDriveDownload, label: "Load", descripcion: "Inserción en BD clínica + log histórico" },
];

function EtlPage() {
  useRequireAuth();
  const queryClient = useQueryClient();

  const { data: stats, isLoading: loadingStats } = useQuery({
    queryKey: ["etl-stats"],
    queryFn: () => etlApi.getStats(),
  });

  const { data: historial, isLoading: loadingHistorial } = useQuery({
    queryKey: ["etl-historial"],
    queryFn: () => etlApi.getJobs(),
  });

  const { mutate: ejecutarETL, isPending, isSuccess, isError } = useMutation({
    mutationFn: () => etlApi.ejecutar(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["etl-stats"] });
      queryClient.invalidateQueries({ queryKey: ["etl-historial"] });
      queryClient.invalidateQueries({ queryKey: ["pacientes"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard-stats"] });
    },
  });

  return (
    <AppShell title="Motor ETL" subtitle="Extracción, transformación y carga de datos clínicos">
      <div className="flex items-center justify-between mb-6">
        <div className="text-sm text-muted-foreground">
          {loadingStats ? (
            <Loader2 className="size-4 animate-spin inline" />
          ) : (
            <>
              Última ejecución:{" "}
              <span className="font-medium text-foreground">{stats?.ultima_ejecucion ?? "—"}</span>
              {" · "}
              <span className="font-medium text-foreground">{stats?.registros_totales ?? 0}</span> registros
              · Tasa de éxito:{" "}
              <span className="font-medium text-foreground">
                {((stats?.tasa_exito ?? 0) * 100).toFixed(1)}%
              </span>
            </>
          )}
        </div>
        <div className="flex items-center gap-3">
          {isSuccess && (
            <span className="text-xs text-success flex items-center gap-1">
              <CheckCircle2 className="size-3.5" /> ETL ejecutado correctamente
            </span>
          )}
          {isError && (
            <span className="text-xs text-critical flex items-center gap-1">
              <XCircle className="size-3.5" /> Error al ejecutar ETL
            </span>
          )}
          <button
            disabled={isPending}
            onClick={() => ejecutarETL()}
            className="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-60"
          >
            {isPending ? <Loader2 className="size-4 animate-spin" /> : <Play className="size-4" />}
            {isPending ? "Ejecutando..." : "Ejecutar ETL ahora"}
          </button>
        </div>
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
              <span className="flex items-center gap-1 text-success">
                <CheckCircle2 className="size-3.5" /> Completado
              </span>
            </div>
            <div className="mt-3 h-1.5 rounded-full bg-muted overflow-hidden">
              <div className="h-full bg-primary rounded-full" style={{ width: "100%" }} />
            </div>
          </Card>
        ))}
      </div>

      <Card>
        <h3 className="font-semibold mb-4">Histórico de ejecuciones</h3>
        {loadingHistorial ? (
          <div className="flex items-center justify-center h-32">
            <Loader2 className="size-6 animate-spin text-primary" />
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-muted-foreground border-b border-border">
                {["#", "Archivo", "Inicio", "Fin", "Procesados", "Errores", "Estado"].map((h) => (
                  <th key={h} className="py-2 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(historial ?? []).map((h) => (
                <tr key={h.id} className="border-b border-border/60 last:border-0">
                  <td className="py-2.5 font-mono text-xs text-muted-foreground">#{h.id}</td>
                  <td className="py-2.5 text-xs text-muted-foreground truncate max-w-[140px]">{h.archivo}</td>
                  <td className="py-2.5 tabular-nums text-xs">{h.fecha_inicio}</td>
                  <td className="py-2.5 tabular-nums text-xs">{h.fecha_fin ?? "—"}</td>
                  <td className="py-2.5 tabular-nums">{h.registros_procesados}</td>
                  <td className="py-2.5 tabular-nums">{h.registros_error}</td>
                  <td className="py-2.5">
                    {h.estado === "completado" ? (
                      <span className="inline-flex items-center gap-1 text-xs text-success">
                        <CheckCircle2 className="size-3.5" /> Éxito
                      </span>
                    ) : h.estado === "error" ? (
                      <span className="inline-flex items-center gap-1 text-xs text-critical">
                        <XCircle className="size-3.5" /> Error
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                        <Clock className="size-3.5" /> {h.estado}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>
    </AppShell>
  );
}
