import pandas as pd
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Columnas obligatorias que debe tener el dataset
REQUIRED_COLUMNS = [
    'id_paciente', 'nombres', 'apellidos', 'edad', 'sexo',
    'peso', 'altura', 'presion_sistolica', 'presion_diastolica',
    'frecuencia_cardiaca', 'glucosa', 'colesterol',
    'saturacion_oxigeno', 'temperatura', 'antecedentes_familiares',
    'fumador', 'consumo_alcohol', 'actividad_fisica',
    'diagnostico_preliminar', 'fecha_consulta'
]


def extract_from_excel(filepath: str) -> dict:
    """
    Lee el archivo Excel del dataset clínico.
    Retorna { df, metadata }
    """
    start = datetime.now()
    logger.info(f"[EXTRACT] Leyendo Excel: {filepath}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Archivo no encontrado: {filepath}")

    try:
        df = pd.read_excel(filepath, engine='openpyxl')
    except Exception as e:
        raise ValueError(f"Error leyendo Excel: {str(e)}")

    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

    elapsed = (datetime.now() - start).total_seconds()
    logger.info(f"[EXTRACT] {len(df)} registros extraídos en {elapsed:.2f}s")

    return {
        'df': df,
        'metadata': {
            'archivo': os.path.basename(filepath),
            'tipo': 'excel',
            'registros_totales': len(df),
            'columnas': list(df.columns),
            'tiempo_extraccion': elapsed,
        }
    }


def extract_from_csv(filepath: str) -> dict:
    """
    Lee un archivo CSV del dataset clínico.
    Retorna { df, metadata }
    """
    start = datetime.now()
    logger.info(f"[EXTRACT] Leyendo CSV: {filepath}")

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Archivo no encontrado: {filepath}")

    try:
        df = pd.read_csv(filepath, encoding='utf-8', sep=None, engine='python')
    except UnicodeDecodeError:
        df = pd.read_csv(filepath, encoding='latin-1', sep=None, engine='python')
    except Exception as e:
        raise ValueError(f"Error leyendo CSV: {str(e)}")

    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]

    elapsed = (datetime.now() - start).total_seconds()
    logger.info(f"[EXTRACT] {len(df)} registros extraídos en {elapsed:.2f}s")

    return {
        'df': df,
        'metadata': {
            'archivo': os.path.basename(filepath),
            'tipo': 'csv',
            'registros_totales': len(df),
            'columnas': list(df.columns),
            'tiempo_extraccion': elapsed,
        }
    }


def validate_columns(df: pd.DataFrame) -> list:
    """
    Verifica que el DataFrame tenga las columnas obligatorias.
    Retorna lista de columnas faltantes.
    """
    df_cols = [c.lower().strip() for c in df.columns]
    missing = [c for c in REQUIRED_COLUMNS if c not in df_cols]
    return missing