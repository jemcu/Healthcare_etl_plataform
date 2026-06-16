# API Endpoints — HealthAnalytics IPS

**Base URL:** `http://localhost:8000/api/`  
**Documentación Swagger:** `http://localhost:8000/api/docs/`  
**Autenticación:** Bearer JWT en header `Authorization`

---

## 🔐 Autenticación (`/api/auth/`)

### POST `/api/auth/login/`
Obtener par de tokens JWT.

**Request:**
```json
{
  "username": "medico01",
  "password": "MiPass123!"
}
```

**Response 200:**
```json
{
  "access":  "eyJhbGci...",
  "refresh": "eyJhbGci...",
  "user": {
    "id": 1,
    "username": "medico01",
    "email": "medico01@ips.com",
    "rol": "Médico"
  }
}
```

---

### POST `/api/auth/refresh/`
Renovar access token.

**Request:**
```json
{ "refresh": "eyJhbGci..." }
```

**Response 200:**
```json
{ "access": "eyJhbGci..." }
```

---

### GET `/api/auth/users/`
Listar todos los usuarios. **Solo Administrador.**

**Response 200:**
```json
[
  { "id": 1, "username": "admin",    "rol": "Administrador", "is_active": true },
  { "id": 2, "username": "medico01", "rol": "Médico",        "is_active": true },
  { "id": 3, "username": "analista01","rol": "Analista",     "is_active": true }
]
```

---

### POST `/api/auth/users/`
Crear usuario. **Solo Administrador.**

**Request:**
```json
{
  "username": "nuevo_medico",
  "email": "nuevo@ips.com",
  "password": "Pass1234!",
  "rol": "Médico"
}
```

---

## 🔄 ETL (`/api/etl/`)

### POST `/api/etl/ejecutar/`
Ejecutar pipeline ETL completo. **Administrador / Analista.**

**Response 202:**
```json
{
  "mensaje": "Pipeline ETL iniciado",
  "tarea_id": "a1b2c3d4-...",
  "estado": "en_proceso"
}
```

---

### GET `/api/etl/estado/`
Estado de la última ejecución ETL.

**Response 200:**
```json
{
  "ultima_ejecucion": "2026-06-10T21:30:00Z",
  "estado": "completado",
  "registros_procesados": 1800,
  "fases_completadas": ["extract", "transform", "load"],
  "duracion_segundos": 42.3,
  "errores": []
}
```

---

### GET `/api/etl/historial/`
Historial de ejecuciones ETL.

**Response 200:**
```json
[
  {
    "id": 5,
    "fecha": "2026-06-10T21:30:00Z",
    "estado": "completado",
    "registros": 1800,
    "usuario": "analista01"
  }
]
```

---

## 📊 Analytics (`/api/analytics/`)

### GET `/api/analytics/estadisticas/`
Estadísticas descriptivas del dataset.

**Response 200:**
```json
{
  "total_pacientes": 1800,
  "distribucion_riesgo": {
    "Alto": 432,
    "Medio": 756,
    "Bajo": 612
  },
  "promedios": {
    "edad": 52.4,
    "imc": 27.3,
    "glucosa": 115.2
  },
  "correlaciones_top": [
    { "variable": "presion_sistolica", "correlacion_con_riesgo": 0.74 },
    { "variable": "glucosa",           "correlacion_con_riesgo": 0.68 }
  ]
}
```

---

### GET `/api/analytics/distribucion/{variable}/`
Distribución de una variable específica.

**Parámetros de ruta:** `variable` (ej: `edad`, `imc`, `glucosa`)

**Response 200:**
```json
{
  "variable": "edad",
  "min": 18,
  "max": 89,
  "media": 52.4,
  "mediana": 51.0,
  "desviacion": 14.2,
  "histograma": [
    { "rango": "18-30", "count": 120 },
    { "rango": "31-45", "count": 380 }
  ]
}
```

---

## 🤖 ML (`/api/ml/`)

### POST `/api/ml/entrenar/`
Entrenar todos los modelos ML. **Administrador / Analista.**

**Request (opcional):**
```json
{
  "modelos": ["logistic_regression", "random_forest", "decision_tree"],
  "test_size": 0.2,
  "random_state": 42
}
```

**Response 200:**
```json
{
  "resultados": {
    "logistic_regression": {
      "accuracy":  0.87,
      "precision": 0.86,
      "recall":    0.85,
      "f1_score":  0.855,
      "roc_auc":   0.91
    },
    "random_forest": {
      "accuracy":  0.92,
      "precision": 0.91,
      "recall":    0.90,
      "f1_score":  0.905,
      "roc_auc":   0.96
    },
    "decision_tree": {
      "accuracy":  0.83,
      "precision": 0.82,
      "recall":    0.81,
      "f1_score":  0.815,
      "roc_auc":   0.87
    }
  },
  "mejor_modelo": "random_forest",
  "modelos_guardados": true
}
```

---

### POST `/api/ml/predecir/`
Predecir riesgo clínico de un paciente. **Todos los roles.**

**Request:**
```json
{
  "modelo": "random_forest",
  "datos": {
    "edad": 65,
    "imc": 31.2,
    "presion_sistolica": 160,
    "presion_diastolica": 100,
    "frecuencia_cardiaca": 95,
    "saturacion_o2": 93,
    "temperatura": 37.8,
    "glucosa": 210,
    "hemoglobina": 11.2,
    "creatinina": 1.8
  }
}
```

**Response 200:**
```json
{
  "riesgo_predicho": "Alto",
  "riesgo_encoded": 2,
  "probabilidades": {
    "Bajo":  0.05,
    "Medio": 0.18,
    "Alto":  0.77
  },
  "modelo_usado": "random_forest",
  "confianza": 0.77,
  "timestamp": "2026-06-10T22:00:00Z"
}
```

---

### GET `/api/ml/modelos/`
Listar modelos entrenados disponibles.

**Response 200:**
```json
[
  {
    "nombre": "random_forest",
    "archivo": "random_forest.pkl",
    "fecha_entrenamiento": "2026-06-10T20:00:00Z",
    "accuracy": 0.92,
    "activo": true
  }
]
```

---

## 👤 Pacientes (`/api/patients/`)

### GET `/api/patients/`
Listar pacientes con filtros.

**Query params:** `riesgo`, `edad_min`, `edad_max`, `genero`, `page`, `page_size`

**Response 200:**
```json
{
  "count": 1800,
  "next": "/api/patients/?page=2",
  "results": [
    {
      "id": 1,
      "id_paciente": "P001",
      "edad": 65,
      "genero": "M",
      "riesgo_clinico": "Alto",
      "imc": 31.2,
      "fecha_ingreso": "2026-01-15"
    }
  ]
}
```

---

### GET `/api/patients/{id}/`
Detalle completo de un paciente.

---

## 📄 Reportes (`/api/reports/`)

### GET `/api/reports/generar/`
Generar reporte. **Todos los roles.**

**Query params:**

| Param    | Valores               | Default |
|----------|-----------------------|---------|
| `formato`| `pdf`, `excel`, `csv` | `pdf`   |
| `tipo`   | `general`, `riesgo`, `ml` | `general` |
| `desde`  | `YYYY-MM-DD`          | —       |
| `hasta`  | `YYYY-MM-DD`          | —       |

**Response:** Archivo binario con `Content-Disposition: attachment`.

---

## 🏠 Dashboard (`/api/dashboard/`)

### GET `/api/dashboard/`
Datos unificados del dashboard. **Todos los roles.**

**Response 200:**
```json
{
  "resumen": {
    "total_pacientes":   1800,
    "alto_riesgo":       432,
    "medio_riesgo":      756,
    "bajo_riesgo":       612,
    "ultimo_etl":        "2026-06-10T21:30:00Z",
    "mejor_modelo_ml":   "random_forest",
    "accuracy_modelo":   0.92
  },
  "tendencias_riesgo": [...],
  "top_variables_riesgo": [...],
  "alertas": [
    { "tipo": "alto_riesgo", "mensaje": "432 pacientes en riesgo alto", "nivel": "critico" }
  ]
}
```

---

## Códigos de Error

| Código | Significado                                  |
|--------|----------------------------------------------|
| 400    | Datos inválidos en el request               |
| 401    | Token JWT inválido o expirado                |
| 403    | Sin permiso para este recurso (rol)         |
| 404    | Recurso no encontrado                        |
| 422    | Error de validación de negocio              |
| 500    | Error interno del servidor                   |

```json
{
  "error": "descripcion_del_error",
  "detalle": "Información adicional del problema",
  "codigo": "ETL_FILE_NOT_FOUND"
}
```