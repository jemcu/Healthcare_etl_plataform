# Directorio: dataset/processed/

Contiene los archivos generados por el pipeline ETL después de procesar
el dataset clínico fuente.

## Archivos generados automáticamente

| Archivo | Descripción |
|---|---|
| `cleaned_data.csv` | Dataset limpio tras la Fase 1 (Extracción y limpieza) |
| `transformed_data.csv` | Dataset transformado tras la Fase 2 (Transformación) |
| `featured_data.csv` | Dataset con features de ingeniería para ML (Fase 3) |
| `etl_metadata.json` | Metadatos del último proceso ETL ejecutado |

## Notas
- Estos archivos se regeneran con cada ejecución del ETL.
- No modificar manualmente.
- Respetar las políticas de privacidad de datos clínicos (anonimización).