import pandas as pd
import numpy as np
import logging
from django.db import connection

logger = logging.getLogger(__name__)

# Features que usará el modelo ML
FEATURE_COLUMNS = [
    'edad', 'peso', 'altura', 'imc',
    'presion_sistolica', 'presion_diastolica',
    'frecuencia_cardiaca', 'glucosa', 'colesterol',
    'saturacion_oxigeno', 'temperatura',
    'fumador', 'consumo_alcohol', 'antecedentes_familiares',
]

TARGET_COLUMN = 'riesgo_enfermedad'

# Mapa de etiquetas para clasificación binaria y multiclase
RIESGO_ENCODING = {
    'Bajo':    0,
    'Medio':   1,
    'Alto':    2,
    'Crítico': 3,
}


def load_dataset_from_db() -> pd.DataFrame:
    """Carga pacientes de la BD en un DataFrame."""
    query = f"""
        SELECT {', '.join(FEATURE_COLUMNS)}, {TARGET_COLUMN}
        FROM patients_paciente
        WHERE riesgo_enfermedad IS NOT NULL
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        cols = [c[0] for c in cursor.description]
        rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=cols)


def preprocess(df: pd.DataFrame) -> dict:
    """
    Prepara X (features) e y (target) listos para Scikit-Learn.
    Retorna { X, y, feature_names, label_encoder }
    """
    logger.info(f"[PREPROCESS] Dataset cargado: {len(df)} registros")

    df = df.copy()

    # Convertir booleanos a int
    for col in ['fumador', 'consumo_alcohol', 'antecedentes_familiares']:
        if col in df.columns:
            df[col] = df[col].astype(int)

    # Convertir numéricas
    for col in FEATURE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Rellenar nulos residuales con mediana
    df[FEATURE_COLUMNS] = df[FEATURE_COLUMNS].fillna(df[FEATURE_COLUMNS].median())

    # Codificar target
    df[TARGET_COLUMN] = df[TARGET_COLUMN].map(RIESGO_ENCODING)
    df.dropna(subset=[TARGET_COLUMN], inplace=True)

    X = df[FEATURE_COLUMNS].values
    y = df[TARGET_COLUMN].astype(int).values

    logger.info(f"[PREPROCESS] X shape: {X.shape} | Clases: {np.unique(y)}")

    return {
        'X': X,
        'y': y,
        'feature_names': FEATURE_COLUMNS,
        'n_clases': len(np.unique(y)),
        'distribucion': {
            label: int((y == code).sum())
            for label, code in RIESGO_ENCODING.items()
        },
    }


def preprocess_single(data: dict) -> np.ndarray:
    """
    Preprocesa un diccionario de entrada (paciente individual)
    para pasarlo al modelo de predicción.
    """
    row = []
    for col in FEATURE_COLUMNS:
        val = data.get(col, 0)
        if isinstance(val, bool):
            val = int(val)
        try:
            row.append(float(val))
        except (ValueError, TypeError):
            row.append(0.0)
    return np.array(row).reshape(1, -1)