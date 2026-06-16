import logging
import os
from datetime import datetime

from .extractor import extract_from_excel, extract_from_csv, validate_columns
from .transformer import transform
from .loader import load_to_database

logger = logging.getLogger(__name__)

# Ruta por defecto del dataset clínico
DEFAULT_DATASET_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
    'dataset', 'raw', 'dataset_clinico.xlsx'
)


def run_etl_pipeline(filepath: str = None, etl_log=None, tipo: str = 'excel') -> dict:
    """
    Orquesta el proceso completo:
        1. Extract  → lee el archivo
        2. Transform → limpia y enriquece
        3. Load     → inserta en BD

    Retorna un dict con el resumen completo de la ejecución.
    """
    start = datetime.now()
    filepath = filepath or DEFAULT_DATASET_PATH

    resultado = {
        'estado': 'ERROR',
        'archivo': filepath,
        'extract': {},
        'transform': {},
        'load': {},
        'tiempo_total': 0,
        'mensaje': '',
    }

    try:
        # ── STEP 1: EXTRACT ───────────────────────────────────────────────
        logger.info("=" * 50)
        logger.info("[ETL] INICIO EXTRACCIÓN")

        if tipo == 'csv':
            extracted = extract_from_csv(filepath)
        else:
            extracted = extract_from_excel(filepath)

        df_raw = extracted['df']
        resultado['extract'] = extracted['metadata']

        # Validar columnas obligatorias
        missing = validate_columns(df_raw)
        if missing:
            raise ValueError(f"Columnas faltantes en el dataset: {missing}")

        # Actualizar log ETL
        if etl_log:
            etl_log.registros_extraidos = len(df_raw)
            etl_log.archivo_origen = os.path.basename(filepath)
            etl_log.tipo_origen = tipo
            etl_log.estado = 'EJECUTANDO'
            etl_log.save(update_fields=['registros_extraidos', 'archivo_origen', 'tipo_origen', 'estado'])

        # ── STEP 2: TRANSFORM ─────────────────────────────────────────────
        logger.info("[ETL] INICIO TRANSFORMACIÓN")
        transformed = transform(df_raw)
        df_clean = transformed['df_clean']
        stats = transformed['stats']
        resultado['transform'] = stats

        # Actualizar log ETL
        if etl_log:
            etl_log.registros_limpios = stats['registros_limpios']
            etl_log.duplicados_removidos = stats['duplicados_removidos']
            etl_log.nulos_tratados = stats['nulos_tratados']
            etl_log.outliers_corregidos = stats['outliers_corregidos']
            etl_log.errores_tipo_corregidos = stats['errores_tipo_corregidos']
            etl_log.save(update_fields=[
                'registros_limpios', 'duplicados_removidos',
                'nulos_tratados', 'outliers_corregidos', 'errores_tipo_corregidos'
            ])

        # ── STEP 3: LOAD ──────────────────────────────────────────────────
        logger.info("[ETL] INICIO CARGA")
        load_result = load_to_database(df_clean, etl_log)
        resultado['load'] = load_result

        # Calcular tiempo total
        elapsed = (datetime.now() - start).total_seconds()
        resultado['tiempo_total'] = round(elapsed, 2)
        resultado['estado'] = 'EXITOSO'
        resultado['mensaje'] = (
            f"ETL completado: {load_result['cargados']} registros cargados "
            f"en {elapsed:.1f}s."
        )

        # Actualizar log ETL — estado final
        if etl_log:
            etl_log.estado = 'EXITOSO'
            etl_log.tiempo_ejecucion = elapsed
            etl_log.mensaje = resultado['mensaje']
            etl_log.fecha_fin = datetime.now()
            etl_log.save(update_fields=['estado', 'tiempo_ejecucion', 'mensaje', 'fecha_fin'])

        logger.info(f"[ETL] FINALIZADO — {resultado['mensaje']}")

    except Exception as e:
        elapsed = (datetime.now() - start).total_seconds()
        resultado['tiempo_total'] = round(elapsed, 2)
        resultado['mensaje'] = str(e)
        logger.error(f"[ETL] ERROR: {e}", exc_info=True)

        if etl_log:
            etl_log.estado = 'ERROR'
            etl_log.tiempo_ejecucion = elapsed
            etl_log.mensaje = str(e)
            etl_log.fecha_fin = datetime.now()
            etl_log.save(update_fields=['estado', 'tiempo_ejecucion', 'mensaje', 'fecha_fin'])

    return resultado