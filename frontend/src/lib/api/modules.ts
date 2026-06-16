import { apiRequest } from "./client";

// ════════════════════════════════════════════════════════════
// DASHBOARD
// ════════════════════════════════════════════════════════════
export interface DashboardStats {
  total_pacientes: number;
  pacientes_alto_riesgo: number;
  modelos_activos: number;
  precision_promedio: number;
  distribucion_riesgo: { nivel: string; cantidad: number }[];
  alertas_recientes: { id: number; mensaje: string; tipo: string; fecha: string }[];
}

export const dashboardApi = {
  getStats: () => apiRequest<DashboardStats>("/api/dashboard/resumen/"),
};

// ════════════════════════════════════════════════════════════
// PACIENTES
// ════════════════════════════════════════════════════════════
export interface Paciente {
  id: number;
  nombre: string;
  edad: number;
  genero: string;
  diagnostico: string;
  nivel_riesgo: "Bajo" | "Medio" | "Alto" | "Crítico";
  fecha_ingreso: string;
  imc: number;
}

export interface PacientesResponse {
  count: number;
  results: Paciente[];
}

export const pacientesApi = {
  list: (page = 1, search = "") =>
    apiRequest<PacientesResponse>(`/api/patients/?page=${page}&search=${search}`),
  get: (id: number) => apiRequest<Paciente>(`/api/patients/${id}/`),
};

// ════════════════════════════════════════════════════════════
// ETL
// ════════════════════════════════════════════════════════════
export interface ETLJob {
  id: number;
  estado: "pendiente" | "procesando" | "completado" | "error";
  archivo: string;
  registros_procesados: number;
  registros_error: number;
  fecha_inicio: string;
  fecha_fin: string | null;
  mensaje_error: string | null;
}

export interface ETLStats {
  total_ejecuciones: number;
  ultima_ejecucion: string;
  registros_totales: number;
  tasa_exito: number;
}

export const etlApi = {
  getStats: () => apiRequest<ETLStats>("/api/etl/estado/"),
  getJobs: () => apiRequest<ETLJob[]>("/api/etl/historial/"),
  ejecutar: () => apiRequest<{ mensaje: string; job_id: number }>("/api/etl/ejecutar/", {
    method: "POST",
  }),
};

// ════════════════════════════════════════════════════════════
// MACHINE LEARNING
// ════════════════════════════════════════════════════════════
export interface MLModel {
  id: number;
  nombre: string;
  tipo: string;
  precision: number;
  recall: number;
  f1_score: number;
  fecha_entrenamiento: string;
  activo: boolean;
}

export interface MLStats {
  modelos_entrenados: number;
  mejor_modelo: string;
  mejor_precision: number;
  ultima_prediccion: string;
}

export const mlApi = {
  getModels: () => apiRequest<MLModel[]>("/api/ml/modelos/"),
  getStats: () => apiRequest<MLStats>("/api/ml/estadisticas/"),
  entrenar: () => apiRequest<{ mensaje: string }>("/api/ml/entrenar/", { method: "POST" }),
};

// ════════════════════════════════════════════════════════════
// REPORTES
// ════════════════════════════════════════════════════════════
export interface Reporte {
  id: number;
  titulo: string;
  tipo: "PDF" | "Excel" | "CSV";
  fecha_generacion: string;
  tamaño: string;
  url_descarga: string;
}

export const reportesApi = {
  list: () => apiRequest<Reporte[]>("/api/reports/"),
  generar: (tipo: "pdf" | "excel" | "csv") =>
    apiRequest<{ url: string }>(`/api/reports/generar/${tipo}/`, { method: "POST" }),
  descargar: (id: number) => {
    window.open(
      `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/api/reports/${id}/descargar/`,
      "_blank"
    );
  },
};
