import { createFileRoute } from "@tanstack/react-router";
import { AppShell, Card } from "@/components/AppShell";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { mlApi } from "@/lib/api";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { Brain, Zap, Target, TrendingUp, Loader2, Play } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useState } from "react";
import { apiRequest } from "@/lib/api/client";

export const Route = createFileRoute("/ml")({
  head: () => ({ meta: [{ title: "Machine Learning | HealthAnalytics" }] }),
  component: MlPage,
});

const clases = ["Bajo", "Medio", "Alto", "Crítico"];

function MlPage() {
  useRequireAuth();
  const queryClient = useQueryClient();
  const [prediccionResult, setPrediccionResult] = useState<{ riesgo: string; probabilidad: number } | null>(null);
  const [formData, setFormData] = useState({
    edad: "", imc: "", glucosa: "", presion_sistolica: "",
    colesterol: "", frecuencia_cardiaca: "", saturacion_oxigeno: "", fumador: "",
  });

  const { data: modelos, isLoading: loadingModelos } = useQuery({
    queryKey: ["ml-modelos"],
    queryFn: () => mlApi.getModels(),
  });

  const { data: mlStats, isLoading: loadingStats } = useQuery({
    queryKey: ["ml-stats"],
    queryFn: () => mlApi.getStats(),
  });

  const { mutate: entrenar, isPending: entrenando } = useMutation({
    mutationFn: () => mlApi.entrenar(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ml-modelos"] });
      queryClient.invalidateQueries({ queryKey: ["ml-stats"] });
    },
  });

  const modeloActivo = modelos?.find((m) => m.activo) ?? modelos?.[0];

  const metricas = modeloActivo
    ? [
        { l: "Accuracy", v: modeloActivo.precision, icon: Target },
        { l: "Precision", v: modeloActivo.precision, icon: Zap },
        { l: "Recall", v: modeloActivo.recall, icon: TrendingUp },
        { l: "F1-Score", v: modeloActivo.f1_score, icon: Brain },
      ]
    : [];

  async function handlePrediccion() {
    try {
      const result = await apiRequest<{ nivel_riesgo: string; probabilidad: number }>(
        "/api/ml/predecir/",
        { method: "POST", body: JSON.stringify(formData) }
      );
      setPrediccionResult({ riesgo: result.nivel_riesgo, probabilidad: result.probabilidad });
    } catch {
      setPrediccionResult(null);
    }
  }

  if (loadingModelos || loadingStats) {
    return (
      <AppShell title="Machine Learning" subtitle="Cargando modelos...">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="size-8 animate-spin text-primary" />
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell title="Machine Learning" subtitle={`Modelo: ${modeloActivo?.nombre ?? "—"} · ${modeloActivo?.tipo ?? ""}`}>
      <div className="flex justify-end mb-4">
        <button
          disabled={entrenando}
          onClick={() => entrenar()}
          className="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 disabled:opacity-60"
        >
          {entrenando ? <Loader2 className="size-4 animate-spin" /> : <Play className="size-4" />}
          {entrenando ? "Entrenando..." : "Reentrenar modelo"}
        </button>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {metricas.map((m) => (
          <Card key={m.l}>
            <div className="flex items-start justify-between">
              <div>
                <div className="text-xs text-muted-foreground uppercase tracking-wide">{m.l}</div>
                <div className="mt-2 text-2xl font-semibold tabular-nums">
                  {(m.v * 100).toFixed(1)}%
                </div>
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

      {/* Lista de modelos */}
      <Card className="mb-6">
        <h3 className="font-semibold mb-4">Modelos entrenados</h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-xs text-muted-foreground border-b border-border">
              {["Nombre", "Tipo", "Precisión", "Recall", "F1", "Entrenado", "Estado"].map((h) => (
                <th key={h} className="py-2 font-medium">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(modelos ?? []).map((m) => (
              <tr key={m.id} className="border-b border-border/60 last:border-0">
                <td className="py-2.5 font-medium">{m.nombre}</td>
                <td className="py-2.5 text-muted-foreground">{m.tipo}</td>
                <td className="py-2.5 tabular-nums">{(m.precision * 100).toFixed(1)}%</td>
                <td className="py-2.5 tabular-nums">{(m.recall * 100).toFixed(1)}%</td>
                <td className="py-2.5 tabular-nums">{(m.f1_score * 100).toFixed(1)}%</td>
                <td className="py-2.5 text-xs text-muted-foreground">{m.fecha_entrenamiento}</td>
                <td className="py-2.5">
                  {m.activo
                    ? <span className="px-2 py-0.5 rounded bg-success/10 text-success text-xs font-medium">Activo</span>
                    : <span className="px-2 py-0.5 rounded bg-muted text-muted-foreground text-xs">Inactivo</span>
                  }
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      <Card>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-semibold">Predicción individual</h3>
            <p className="text-xs text-muted-foreground">
              Ingresa variables clínicas y obtén probabilidad de riesgo
            </p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { label: "Edad", key: "edad", placeholder: "62", unit: "años" },
            { label: "IMC", key: "imc", placeholder: "28.4", unit: "kg/m²" },
            { label: "Glucosa", key: "glucosa", placeholder: "165", unit: "mg/dL" },
            { label: "PA sistólica", key: "presion_sistolica", placeholder: "148", unit: "mmHg" },
            { label: "Colesterol", key: "colesterol", placeholder: "230", unit: "mg/dL" },
            { label: "Frec. cardiaca", key: "frecuencia_cardiaca", placeholder: "82", unit: "bpm" },
            { label: "SatO₂", key: "saturacion_oxigeno", placeholder: "94", unit: "%" },
            { label: "Fumador", key: "fumador", placeholder: "true / false", unit: "" },
          ].map((f) => (
            <label key={f.label} className="block">
              <span className="text-xs text-muted-foreground">
                {f.label} <span className="text-muted-foreground/60">{f.unit}</span>
              </span>
              <input
                value={formData[f.key as keyof typeof formData]}
                onChange={(e) => setFormData((prev) => ({ ...prev, [f.key]: e.target.value }))}
                className="mt-1 w-full h-9 px-3 rounded-md border border-border bg-background text-sm outline-none focus:ring-2 ring-primary/40"
                placeholder={f.placeholder}
              />
            </label>
          ))}
        </div>
        <div className="flex items-center gap-3 mt-5">
          <button
            onClick={handlePrediccion}
            className="px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90"
          >
            Ejecutar predicción
          </button>
          {prediccionResult && (
            <div className={`ml-auto flex items-center gap-2 px-3 py-2 rounded-lg ring-1 ${
              prediccionResult.riesgo === "Crítico" || prediccionResult.riesgo === "Alto"
                ? "bg-critical/10 ring-critical/25 text-critical"
                : "bg-success/10 ring-success/25 text-success"
            }`}>
              <div className="size-2 rounded-full bg-current animate-pulse" />
              <span className="text-sm font-medium">
                Riesgo {prediccionResult.riesgo} · {(prediccionResult.probabilidad * 100).toFixed(0)}% probabilidad
              </span>
            </div>
          )}
        </div>
      </Card>
    </AppShell>
  );
}
