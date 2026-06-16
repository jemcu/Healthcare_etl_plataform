# Arquitectura del Sistema — HealthAnalytics IPS

## Descripción General

HealthAnalytics IPS es una plataforma backend de analítica clínica con capacidades de
machine learning para detección de riesgo en pacientes. Está construida sobre
**Django REST Framework** y expone una API RESTful consumida por frontends externos.

---

## Stack Tecnológico

| Capa             | Tecnología                              |
|------------------|-----------------------------------------|
| Lenguaje         | Python 3.12                             |
| Framework Web    | Django 4.2 + Django REST Framework 3.15 |
| Autenticación    | JWT via `djangorestframework-simplejwt` |
| Base de datos    | PostgreSQL 15                           |
| Caché / Broker   | Redis 7                                 |
| Tareas async     | Celery 5.3 + Celery Beat                |
| ML               | Scikit-Learn 1.5                        |
| Data processing  | Pandas 2.2 + NumPy 1.26                 |
| Reportes         | ReportLab 4.2 (PDF) + xlsxwriter 3.2   |
| Documentación API| drf-spectacular 0.27 (OpenAPI/Swagger)  |
| Contenedores     | Docker + Docker Compose                 |

---

## Estructura de Módulos (Django Apps)

```
backend/
└── app/
    ├── authentication/     # JWT, roles, permisos
    ├── etl/                # Pipeline ETL de 3 fases
    ├── analytics/          # Estadísticas y análisis descriptivo
    ├── ml/                 # Modelos de ML (entrenamiento e inferencia)
    ├── patients/           # Gestión de pacientes
    ├── reports/            # Generación PDF / Excel / CSV
    └── dashboard/          # Endpoint unificado del dashboard
```

---

## Roles y Permisos

| Rol           | Permisos                                                           |
|---------------|--------------------------------------------------------------------|
| Administrador | Acceso total: usuarios, ETL, ML, reportes, dashboard              |
| Médico        | Lectura de pacientes, predicciones, dashboard, reportes propios    |
| Analista      | ETL, analytics, ML (solo inferencia), reportes globales, dashboard |

---

## Flujo de Datos Principal

```
Dataset Excel (.xlsx)
        │
        ▼
┌───────────────┐
│  ETL Fase 1   │  Extracción + Limpieza (Pandas)
│  (Extract)    │  → cleaned_data.csv
└──────┬────────┘
       │
       ▼
┌───────────────┐
│  ETL Fase 2   │  Transformación + Normalización
│  (Transform)  │  → transformed_data.csv
└──────┬────────┘
       │
       ▼
┌───────────────┐
│  ETL Fase 3   │  Feature Engineering + Carga a BD
│  (Load)       │  → featured_data.csv → PostgreSQL
└──────┬────────┘
       │
       ▼
┌───────────────┐
│  ML Training  │  Logistic Regression / Random Forest / Decision Tree
│               │  → modelos .pkl guardados en ml_models/
└──────┬────────┘
       │
       ▼
┌───────────────┐
│  Predicción   │  Inferencia en tiempo real por paciente
│  (Inference)  │  → riesgo_clinico: Alto / Medio / Bajo
└──────┬────────┘
       │
       ▼
┌───────────────┐
│  Dashboard +  │  Métricas agregadas + reportes PDF/Excel/CSV
│  Reportes     │
└───────────────┘
```

---

## Endpoints Principales

| Método | Endpoint                          | Descripción                        |
|--------|-----------------------------------|------------------------------------|
| POST   | `/api/auth/login/`                | Obtener JWT                        |
| POST   | `/api/auth/refresh/`              | Refrescar token                    |
| GET    | `/api/auth/users/`                | Listar usuarios (Admin)            |
| POST   | `/api/etl/ejecutar/`              | Ejecutar pipeline ETL completo     |
| GET    | `/api/etl/estado/`                | Estado del último ETL              |
| GET    | `/api/analytics/estadisticas/`    | Estadísticas descriptivas          |
| POST   | `/api/ml/entrenar/`               | Entrenar modelos ML                |
| POST   | `/api/ml/predecir/`               | Predecir riesgo de un paciente     |
| GET    | `/api/ml/modelos/`                | Listar modelos disponibles         |
| GET    | `/api/patients/`                  | Listar pacientes                   |
| GET    | `/api/patients/{id}/`             | Detalle de paciente                |
| GET    | `/api/reports/generar/`           | Generar reporte (PDF/Excel/CSV)    |
| GET    | `/api/dashboard/`                 | Dashboard unificado                |

Documentación interactiva disponible en `/api/docs/` (Swagger UI).

---

## Variables de Entorno Requeridas

```env
SECRET_KEY=tu-clave-secreta
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=healthcare_db
DB_USER=healthcare_user
DB_PASSWORD=healthcare_pass
DB_HOST=localhost
DB_PORT=5432

REDIS_URL=redis://localhost:6379/0

DATASET_PATH=dataset/raw/dataset_clinico.xlsx
ML_MODELS_PATH=ml_models/
```

---

## Consideraciones de Seguridad

- Todos los endpoints requieren autenticación JWT (excepto `/api/auth/login/`).
- Los tokens expiran en 60 minutos; se renuevan con refresh token (7 días).
- Los datos clínicos se manejan según normativas de privacidad (anonimización en logs).
- CORS configurado con `django-cors-headers` para dominios autorizados.
- Contraseñas hasheadas con PBKDF2 (Django default).