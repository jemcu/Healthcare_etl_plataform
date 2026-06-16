import pandas as pd
import numpy as np
from django.db import connection


def get_dataframe_from_db():
    """
    Carga todos los pacientes desde la BD en un DataFrame de Pandas.
    """
    query = """
        SELECT edad, sexo, peso, altura, imc, presion_sistolica,
               presion_diastolica, frecuencia_cardiaca, glucosa, colesterol,
               saturacion_oxigeno, temperatura, fumador, consumo_alcohol,
               actividad_fisica, diagnostico_preliminar, riesgo_enfermedad,
               antecedentes_familiares
        FROM patients_paciente
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
    return pd.DataFrame(rows, columns=columns)


def calcular_estadisticas_descriptivas():
    """
    Retorna media, mediana, moda y desviación estándar
    de las variables numéricas clínicas.
    """
    df = get_dataframe_from_db()

    if df.empty:
        return {}

    numeric_cols = [
        'edad', 'peso', 'altura', 'imc',
        'presion_sistolica', 'presion_diastolica',
        'frecuencia_cardiaca', 'glucosa', 'colesterol',
        'saturacion_oxigeno', 'temperatura'
    ]

    # Solo columnas presentes en el df
    numeric_cols = [c for c in numeric_cols if c in df.columns]
    df_num = df[numeric_cols].apply(pd.to_numeric, errors='coerce')

    resultado = {}
    for col in numeric_cols:
        serie = df_num[col].dropna()
        if serie.empty:
            continue
        resultado[col] = {
            'media': round(float(serie.mean()), 2),
            'mediana': round(float(serie.median()), 2),
            'moda': round(float(serie.mode().iloc[0]), 2) if not serie.mode().empty else None,
            'desviacion_std': round(float(serie.std()), 2),
            'minimo': round(float(serie.min()), 2),
            'maximo': round(float(serie.max()), 2),
            'total_registros': int(serie.count()),
        }

    return resultado