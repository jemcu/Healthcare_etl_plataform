# Manual de Usuario — HealthAnalytics IPS

## ¿Qué es HealthAnalytics IPS?

HealthAnalytics IPS es una plataforma de analítica clínica que permite a equipos
médicos y de análisis procesar datos de pacientes, aplicar modelos de machine learning
para detección de riesgo, y generar reportes automatizados.

---

## Primeros Pasos

### 1. Levantar el sistema

```bash
# Clonar el repositorio
git clone <repo-url>
cd healthcare-etl-plataform

# Copiar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# Levantar con Docker
cd docker
docker compose -f docker-composer.yml up -d

# Ver logs
docker compose -f docker-composer.yml logs -f web
```

El sistema estará disponible en: `http://localhost:8000`  
Swagger UI: `http://localhost:8000/api/docs/`

---

### 2. Colocar el dataset

Copia tu archivo Excel clínico en:

```
dataset/raw/dataset_clinico.xlsx
```

Luego valídalo:

```bash
python dataset/validate_dataset.py
```

---

### 3. Primer login

Usuario por defecto creado automáticamente al iniciar:

| Campo    | Valor                     |
|----------|---------------------------|
| Username | `admin`                   |
| Password | `Admin1234!`              |
| Rol      | Administrador             |

**⚠️ Cambia la contraseña inmediatamente después del primer login.**

```bash
POST /api/auth/login/
{
  "username": "admin",
  "password": "Admin1234!"
}
```

Guarda el `access` token para usarlo en las demás peticiones:

```
Authorization: Bearer eyJhbGci...
```

---

## Flujo de Trabajo Recomendado

```
1. Validar dataset  →  python dataset/validate_dataset.py
2. Ejecutar ETL     →  POST /api/etl/ejecutar/
3. Verificar ETL    →  GET  /api/etl/estado/
4. Entrenar ML      →  POST /api/ml/entrenar/
5. Ver dashboard    →  GET  /api/dashboard/
6. Predecir riesgo  →  POST /api/ml/predecir/
7. Generar reporte  →  GET  /api/reports/generar/?formato=pdf
```

---

## Guía por Rol

### 👨‍💼 Administrador

Acceso completo al sistema. Responsabilidades:

- Crear y gestionar usuarios (`GET/POST /api/auth/users/`)
- Supervisar ejecuciones ETL
- Monitorear modelos ML
- Ver dashboard global

**Crear un médico:**
```json
POST /api/auth/users/
{
  "username": "dr_rodriguez",
  "email": "dr.rodriguez@ips.com",
  "password": "MedPass2026!",
  "rol": "Médico"
}
```

---

### 🩺 Médico

Acceso a pacientes, predicciones y reportes propios.

**Ver pacientes en riesgo alto:**
```
GET /api/patients/?riesgo=Alto&page=1
```

**Predecir riesgo de un paciente:**
```json
POST /api/ml/predecir/
{
  "modelo": "random_forest",
  "datos": {
    "edad": 72,
    "presion_sistolica": 170,
    "glucosa": 250,
    ...
  }
}
```

**Generar reporte de mis pacientes en PDF:**
```
GET /api/reports/generar/?formato=pdf&tipo=riesgo
```

---

### 📊 Analista

Acceso a ETL, analytics, ML y reportes globales.

**Ejecutar ETL:**
```bash
POST /api/etl/ejecutar/
Authorization: Bearer <token>
```

**Ver estadísticas:**
```
GET /api/analytics/estadisticas/
GET /api/analytics/distribucion/glucosa/
```

**Reentrenar modelos:**
```json
POST /api/ml/entrenar/
{
  "modelos": ["random_forest", "logistic_regression"],
  "test_size": 0.25
}
```

**Exportar datos a Excel:**
```
GET /api/reports/generar/?formato=excel&tipo=general
```

---

## Interpretación del Dashboard

| Métrica             | Descripción                                         |
|---------------------|-----------------------------------------------------|
| `total_pacientes`   | Pacientes cargados desde el último ETL              |
| `alto_riesgo`       | Pacientes clasificados con riesgo clínico alto      |
| `accuracy_modelo`   | Precisión del mejor modelo ML en datos de prueba    |
| `ultimo_etl`        | Fecha/hora de la última ejecución ETL exitosa       |
| `alertas`           | Notificaciones automáticas de condiciones críticas  |

---

## Interpretación de Predicciones ML

| Riesgo | Probabilidad sugerida | Acción recomendada                        |
|--------|-----------------------|-------------------------------------------|
| Bajo   | < 30%                 | Seguimiento rutinario                     |
| Medio  | 30% – 70%             | Evaluación prioritaria en 48h             |
| Alto   | > 70%                 | Atención inmediata / hospitalización      |

> **Nota:** Las predicciones son un apoyo al criterio clínico, no un reemplazo.
> Siempre valide con el juicio médico del profesional tratante.

---

## Solución de Problemas Frecuentes

### El ETL falla con "archivo no encontrado"
→ Verifica que el archivo exista en `dataset/raw/dataset_clinico.xlsx`  
→ Ejecuta `python dataset/validate_dataset.py` para más detalles

### Token expirado (401 Unauthorized)
→ Usa `POST /api/auth/refresh/` con tu refresh token  
→ Si el refresh también expiró, haz login de nuevo

### Modelos ML no disponibles para predicción
→ Ejecuta primero `POST /api/ml/entrenar/`  
→ Verifica que el ETL haya cargado datos en la BD

### Error 403 Forbidden en un endpoint
→ Tu rol no tiene permiso para ese recurso  
→ Contacta al Administrador para revisar tu rol

---

## Soporte

- Swagger UI: `http://localhost:8000/api/docs/`
- Logs del servidor: `logs/error.log`
- Estado del sistema: `GET /api/dashboard/`