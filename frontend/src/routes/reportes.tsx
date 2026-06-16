import { createFileRoute } from "@tanstack/react-router";
import { AppShell, Card } from "@/components/AppShell";
import { useQuery, useMutation } from "@tanstack/react-query";
import { reportesApi } from "@/lib/api";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { FileText, FileSpreadsheet, FileType2, Download, Loader2 } from "lucide-react";

export const Route = createFileRoute("/reportes")({
  head: () => ({ meta: [{ title: "Reportes | HealthAnalytics" }] }),
  component: ReportesPage,
});

const tipoColor: Record<string, string> = {
  PDF: "bg-critical/10 text-critical",
  Excel: "bg-success/10 text-success",
  CSV: "bg-primary/10 text-primary",
};

function ReportesPage() {
  useRequireAuth();

  const { data: reportes, isLoading } = useQuery({
    queryKey: ["reportes"],
    queryFn: () => reportesApi.list(),
  });

  const { mutate: generarPDF, isPending: generandoPDF } = useMutation({
    mutationFn: () => reportesApi.generar("pdf"),
    onSuccess: (data) => window.open(data.url, "_blank"),
  });

  const { mutate: generarExcel, isPending: generandoExcel } = useMutation({
    mutationFn: () => reportesApi.generar("excel"),
    onSuccess: (data) => window.open(data.url, "_blank"),
  });

  const { mutate: generarCSV, isPending: generandoCSV } = useMutation({
    mutationFn: () => reportesApi.generar("csv"),
    onSuccess: (data) => window.open(data.url, "_blank"),
  });

  return (
    <AppShell title="Reportes" subtitle="Exporta información clínica en PDF, Excel o CSV">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card
          className="hover:border-primary/40 transition-colors cursor-pointer"
          onClick={() => generarPDF()}
        >
          <div className="flex items-center gap-3">
            <div className="size-11 rounded-lg bg-primary/10 text-primary grid place-items-center">
              {generandoPDF ? <Loader2 className="size-5 animate-spin" /> : <FileType2 className="size-5" />}
            </div>
            <div>
              <div className="font-semibold">Exportar PDF</div>
              <div className="text-xs text-muted-foreground">Informes formales con branding IPS</div>
            </div>
          </div>
        </Card>

        <Card
          className="hover:border-primary/40 transition-colors cursor-pointer"
          onClick={() => generarExcel()}
        >
          <div className="flex items-center gap-3">
            <div className="size-11 rounded-lg bg-primary/10 text-primary grid place-items-center">
              {generandoExcel ? <Loader2 className="size-5 animate-spin" /> : <FileSpreadsheet className="size-5" />}
            </div>
            <div>
              <div className="font-semibold">Exportar Excel</div>
              <div className="text-xs text-muted-foreground">Datos tabulares con fórmulas</div>
            </div>
          </div>
        </Card>

        <Card
          className="hover:border-primary/40 transition-colors cursor-pointer"
          onClick={() => generarCSV()}
        >
          <div className="flex items-center gap-3">
            <div className="size-11 rounded-lg bg-primary/10 text-primary grid place-items-center">
              {generandoCSV ? <Loader2 className="size-5 animate-spin" /> : <FileText className="size-5" />}
            </div>
            <div>
              <div className="font-semibold">Exportar CSV</div>
              <div className="text-xs text-muted-foreground">Para herramientas externas y BI</div>
            </div>
          </div>
        </Card>
      </div>

      <Card>
        <h3 className="font-semibold mb-4">Reportes generados</h3>
        {isLoading ? (
          <div className="flex items-center justify-center h-40">
            <Loader2 className="size-6 animate-spin text-primary" />
          </div>
        ) : (reportes ?? []).length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">
            No hay reportes generados aún. Usa los botones de arriba para generar uno.
          </p>
        ) : (
          <div className="divide-y divide-border">
            {(reportes ?? []).map((r) => (
              <div key={r.id} className="flex items-center gap-4 py-3 first:pt-0 last:pb-0">
                <div className="size-10 rounded-lg bg-muted grid place-items-center text-muted-foreground">
                  <FileText className="size-5" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-medium truncate">{r.titulo}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${tipoColor[r.tipo] ?? "bg-muted text-muted-foreground"}`}>
                      {r.tipo}
                    </span>
                  </div>
                  <div className="text-xs text-muted-foreground mt-0.5">{r.tamaño}</div>
                </div>
                <div className="text-xs text-muted-foreground tabular-nums">{r.fecha_generacion}</div>
                <button
                  onClick={() => reportesApi.descargar(r.id)}
                  className="size-9 grid place-items-center rounded-md border border-border hover:bg-muted"
                >
                  <Download className="size-4" />
                </button>
              </div>
            ))}
          </div>
        )}
      </Card>
    </AppShell>
  );
}
