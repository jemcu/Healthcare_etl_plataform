// Cliente base
export { apiRequest, tokens } from "./client";

// Auth
export { login, logout, getCurrentUser, isAuthenticated } from "./auth";
export type { LoginPayload, AuthUser, LoginResponse } from "./auth";

// Módulos
export { dashboardApi, pacientesApi, etlApi, mlApi, reportesApi } from "./modules";
export type {
  DashboardStats,
  Paciente,
  PacientesResponse,
  ETLJob,
  ETLStats,
  MLModel,
  MLStats,
  Reporte,
} from "./modules";
