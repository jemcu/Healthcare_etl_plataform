# Flujo ETL — HealthAnalytics IPS

## Descripción

El pipeline ETL procesa el dataset clínico fuente en **tres fases secuenciales**,
transformando los datos crudos del Excel en registros listos para análisis y ML.

---

## Fase 1 — Extracción y Limpieza (`Extract`)

**Entrada:** `dataset/raw/dataset_clinico.xlsx`  
**Salida:** `dataset/processed/cleaned_data.csv`

### Operaciones

| Operación                     | Detalle                                               |
|-------------------------------|-------------------------------------------------------|
| Carga del Excel               | `pandas.read_excel()` con engine `openpyxl`          |
| Normalización de columnas     | `.lower().strip()` en nombres de columnas             |
| Eliminación de duplicados     | `drop_duplicates()` por `id_paciente`                |
| Imputación de nulos numéricos | Mediana por columna                                   |
| Imputación de nulos categóric.| Moda por columna                                      |
| Conversión de tipos           | `edad`, `peso_kg`, `talla_cm` → numérico             |
| Validación de rangos          | Detección de outliers (IQR) sin eliminación forzada  |
| Log de limpieza               | Registro de filas modificadas / eliminadas            |

### Código clave

```python
# app/etl/phases/extract.py
df = pd.read_excel(settings.DATASET_PATH, engine='openpyxl')
df.columns = df.columns.str.lower().str.strip()
df = df.drop_duplicates(subset=['id_paciente'])
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')
    df[col].fillna(df[col].median(), inplace=True)
df.to_csv(CLEANED_PATH, index=False)
```

---

## Fase 2 — Transformación (`Transform`)

**Entrada:** `dataset/processed/cleaned_data.csv`  
**Salida:** `dataset/processed/transformed_data.csv`

### Operaciones

| Operación                   | Detalle                                              |
|-----------------------------|------------------------------------------------------|
| Cálculo de IMC              | `peso_kg / (talla_cm/100)²`                         |
| Clasificación presión       | Hipertensión, Normal, Hipotensión                   |
| Grupos etarios              | Pediátrico, Adulto Joven, Adulto, Adulto Mayor      |
| Encoding de género          | `LabelEncoder` (0/1)                                |
| Encoding de riesgo_clinico  | `LabelEncoder` (0=Bajo, 1=Medio, 2=Alto)            |
| Normalización numérica      | `StandardScaler` en signos vitales y laboratorio    |
| One-Hot Encoding            | Variables categóricas adicionales con `pd.get_dummies` |

### Variables generadas

```
imc                  → Índice de Masa Corporal
clasificacion_presion → 0=Hipotensión, 1=Normal, 2=Hipertensión
grupo_etario         → 0=Pediátrico, 1=Adulto Joven, 2=Adulto, 3=Mayor
riesgo_encoded       → 0=Bajo, 1=Medio, 2=Alto  (target variable)
```

---

## Fase 3 — Carga (`Load`)

**Entrada:** `dataset/processed/transformed_data.csv`  
**Salida:** PostgreSQL (tabla `patients_paciente`) + `dataset/processed/featured_data.csv`

### Operaciones

| Operación                  | Detalle                                               |
|----------------------------|-------------------------------------------------------|
| Selección de features ML   | Top features por correlación con `riesgo_encoded`    |
| Generación de features     | Interacciones entre variables (presión × frecuencia) |
| Carga a PostgreSQL         | `bulk_create()` con batch de 500 registros           |
| Actualización de metadata  | JSON con timestamp, nº registros, columnas usadas    |
| Señal de completitud       | Registro en tabla `etl_ejecucion`                    |

### Features seleccionados para ML

```python
FEATURES_ML = [
    'edad', 'imc', 'presion_sistolica', 'presion_diastolica',
    'frecuencia_cardiaca', 'saturacion_o2', 'temperatura',
    'glucosa', 'hemoglobina', 'creatinina',
    'grupo_etario', 'clasificacion_presion', 'genero_encoded'
]
TARGET = 'riesgo_encoded'
```

---

## Ejecución del ETL

### Via API

```bash
POST /api/etl/ejecutar/
Authorization: Bearer <jwt_token>
Content-Type: application/json

{}
```

### Via management command

```bash
python manage.py ejecutar_etl
python manage.py ejecutar_etl --fase 1   # Solo fase 1
python manage.py ejecutar_etl --fase 2   # Solo fase 2
python manage.py ejecutar_etl --fase 3   # Solo fase 3
```

### Via validación previa

```bash
python dataset/validate_dataset.py
```

---

## Monitoreo

El estado del ETL se consulta en:

```
GET /api/etl/estado/
```

Respuesta:

```json
{
  "ultima_ejecucion": "2026-06-10T21:30:00",
  "estado": "completado",
  "registros_procesados": 1800,
  "fases_completadas": ["extract", "transform", "load"],
  "duracion_segundos": 42.3,
  "errores": []
}
```

---

## Manejo de Errores

| Error                         | Comportamiento                                     |
|-------------------------------|----------------------------------------------------|
| Archivo Excel no encontrado   | HTTP 404 + log crítico                             |
| Columna requerida faltante    | HTTP 400 + detalle de columnas faltantes           |
| Error en fase intermedia      | Rollback de BD + estado `fallido` en `etl_ejecucion` |
| Timeout en carga masiva       | Retry automático con batch menor (100 registros)  |