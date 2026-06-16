import pandas as pd
import numpy as np
import logging
import re

logger = logging.getLogger(__name__)

# ── Rangos clínicos válidos ────────────────────────────────────────────────────
CLINICAL_RANGES = {
    'edad':                 (0,    120),
    'peso':                 (2,    300),
    'altura':               (0.5,  2.5),
    'presion_sistolica':    (60,   250),
    'presion_diastolica':   (40,   150),
    'frecuencia_cardiaca':  (30,   220),
    'glucosa':              (30,   600),
    'colesterol':           (50,   500),
    'saturacion_oxigeno':   (60,   100),
    'temperatura':          (30,    43),
}

# ── Mapas de normalización ────────────────────────────────────────────────────
SEXO_MAP = {
    'm': 'Masculino', 'masculino': 'Masculino', 'hombre': 'Masculino',
    'male': 'Masculino', 'h': 'Masculino',
    'f': 'Femenino', 'femenino': 'Femenino', 'mujer': 'Femenino',
    'female': 'Femenino',
}

DIAGNOSTICO_MAP = {
    'hipertencion': 'Hipertensión',
    'hipertensíon': 'Hipertensión',
    'hipertension': 'Hipertensión',
    'hipertensión': 'Hipertensión',
    'diabetis': 'Diabetes',
    'diabetes mellitus': 'Diabetes',
    'obesidad morbida': 'Obesidad mórbida',
    'obesidad morbída': 'Obesidad mórbida',
    'enf. coronaria': 'Enfermedad coronaria',
    'enf coronaria': 'Enfermedad coronaria',
}

ACTIVIDAD_MAP = {
    'sedentario': 'Sedentario', 'sedentaria': 'Sedentario',
    'leve': 'Leve', 'ligero': 'Leve',
    'moderado': 'Moderado', 'moderada': 'Moderado',
    'activo': 'Activo', 'activa': 'Activo', 'alto': 'Activo',
    'muy activo': 'Muy activo', 'muy activa': 'Muy activo',
}

BOOL_TRUE  = {'si', 'sí', 'yes', '1', 'true', 'verdadero', 'v', 's'}
BOOL_FALSE = {'no', '0', 'false', 'falso', 'f', 'n'}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _to_bool(val) -> bool | None:
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return bool(val)
    if isinstance(val, str):
        v = val.strip().lower()
        if v in BOOL_TRUE:
            return True
        if v in BOOL_FALSE:
            return False
    return None


def _calcular_imc(peso, altura) -> float | None:
    try:
        peso, altura = float(peso), float(altura)
        if altura > 0 and peso > 0:
            return round(peso / (altura ** 2), 2)
    except (ValueError, TypeError):
        pass
    return None


def _clasificar_imc(imc) -> str:
    if imc is None or pd.isna(imc):
        return 'Sin datos'
    if imc < 18.5:
        return 'Bajo peso'
    if imc < 25:
        return 'Normal'
    if imc < 30:
        return 'Sobrepeso'
    return 'Obesidad'


def _clasificar_riesgo(row) -> str:
    """
    Clasifica el riesgo en Bajo / Medio / Alto / Crítico
    según variables clínicas combinadas.
    """
    score = 0

    # Presión sistólica
    ps = row.get('presion_sistolica')
    if pd.notna(ps):
        if ps > 180:   score += 4
        elif ps > 160: score += 3
        elif ps > 140: score += 2
        elif ps > 120: score += 1

    # Glucosa
    gl = row.get('glucosa')
    if pd.notna(gl):
        if gl > 300:   score += 4
        elif gl > 200: score += 3
        elif gl > 126: score += 2
        elif gl > 100: score += 1

    # Saturación O2
    so = row.get('saturacion_oxigeno')
    if pd.notna(so):
        if so < 85:    score += 4
        elif so < 90:  score += 3
        elif so < 94:  score += 2

    # IMC
    imc = row.get('imc')
    if pd.notna(imc):
        if imc >= 40:  score += 3
        elif imc >= 35: score += 2
        elif imc >= 30: score += 1
        elif imc < 18.5: score += 1

    # Factores de riesgo adicionales
    if row.get('fumador'):        score += 1
    if row.get('consumo_alcohol'): score += 1
    if row.get('antecedentes_familiares'): score += 1

    # Edad
    edad = row.get('edad')
    if pd.notna(edad):
        if edad > 75:  score += 2
        elif edad > 60: score += 1

    if score >= 8:  return 'Crítico'
    if score >= 5:  return 'Alto'
    if score >= 2:  return 'Medio'
    return 'Bajo'


# ── Pipeline principal ────────────────────────────────────────────────────────

def transform(df: pd.DataFrame) -> dict:
    """
    Ejecuta el pipeline completo de transformación.
    Retorna { df_clean, stats }
    """
    stats = {
        'registros_iniciales': len(df),
        'duplicados_removidos': 0,
        'nulos_tratados': 0,
        'outliers_corregidos': 0,
        'errores_tipo_corregidos': 0,
    }

    df = df.copy()

    # 1. Eliminar duplicados
    before = len(df)
    df.drop_duplicates(subset=['id_paciente'], keep='first', inplace=True)
    stats['duplicados_removidos'] = before - len(df)
    logger.info(f"[TRANSFORM] Duplicados removidos: {stats['duplicados_removidos']}")

    # 2. Convertir tipos numéricos — corregir "Treinta", "Alta", etc.
    numeric_cols = [
        'edad', 'peso', 'altura', 'presion_sistolica', 'presion_diastolica',
        'frecuencia_cardiaca', 'glucosa', 'colesterol', 'saturacion_oxigeno',
        'temperatura', 'imc'
    ]
    for col in numeric_cols:
        if col in df.columns:
            before_nulls = df[col].isna().sum()
            df[col] = pd.to_numeric(df[col], errors='coerce')
            after_nulls = df[col].isna().sum()
            stats['errores_tipo_corregidos'] += max(0, after_nulls - before_nulls)

    logger.info(f"[TRANSFORM] Errores de tipo corregidos: {stats['errores_tipo_corregidos']}")

    # 3. Validar y corregir outliers fuera de rangos clínicos
    for col, (low, high) in CLINICAL_RANGES.items():
        if col in df.columns:
            mask = (df[col] < low) | (df[col] > high)
            count = mask.sum()
            if count > 0:
                df.loc[mask, col] = np.nan
                stats['outliers_corregidos'] += int(count)

    logger.info(f"[TRANSFORM] Outliers corregidos: {stats['outliers_corregidos']}")

    # 4. Tratar nulos — imputación con media/mediana/moda
    nulos_antes = df.isnull().sum().sum()

    for col in ['edad', 'peso', 'altura', 'presion_sistolica', 'presion_diastolica',
                'frecuencia_cardiaca', 'glucosa', 'colesterol', 'saturacion_oxigeno',
                'temperatura']:
        if col in df.columns and df[col].isna().any():
            df[col].fillna(df[col].median(), inplace=True)

    for col in ['sexo', 'actividad_fisica', 'diagnostico_preliminar']:
        if col in df.columns and df[col].isna().any():
            mode = df[col].mode()
            df[col].fillna(mode[0] if not mode.empty else 'Sin datos', inplace=True)

    for col in ['fumador', 'consumo_alcohol', 'antecedentes_familiares']:
        if col in df.columns and df[col].isna().any():
            df[col].fillna(False, inplace=True)

    nulos_despues = df.isnull().sum().sum()
    stats['nulos_tratados'] = int(nulos_antes - nulos_despues)
    logger.info(f"[TRANSFORM] Nulos tratados: {stats['nulos_tratados']}")

    # 5. Normalizar sexo
    if 'sexo' in df.columns:
        df['sexo'] = df['sexo'].astype(str).str.strip().str.lower().map(
            lambda x: SEXO_MAP.get(x, 'Sin datos')
        )

    # 6. Normalizar diagnósticos (errores ortográficos)
    if 'diagnostico_preliminar' in df.columns:
        df['diagnostico_preliminar'] = df['diagnostico_preliminar'].astype(str).apply(
            lambda x: DIAGNOSTICO_MAP.get(x.strip().lower(), x.strip().title())
        )

    # 7. Normalizar actividad física
    if 'actividad_fisica' in df.columns:
        df['actividad_fisica'] = df['actividad_fisica'].astype(str).str.strip().str.lower().map(
            lambda x: ACTIVIDAD_MAP.get(x, x.strip().title())
        )

    # 8. Convertir booleanos
    for col in ['fumador', 'consumo_alcohol', 'antecedentes_familiares']:
        if col in df.columns:
            df[col] = df[col].apply(_to_bool).fillna(False).astype(bool)

    # 9. Convertir fecha
    if 'fecha_consulta' in df.columns:
        df['fecha_consulta'] = pd.to_datetime(df['fecha_consulta'], errors='coerce')
        df['fecha_consulta'].fillna(pd.Timestamp.now(), inplace=True)

    # 10. Calcular / recalcular IMC
    if 'peso' in df.columns and 'altura' in df.columns:
        df['imc'] = df.apply(
            lambda r: _calcular_imc(r['peso'], r['altura']), axis=1
        )
        df['imc'].fillna(df['imc'].median(), inplace=True)

    # 11. Clasificar IMC
    df['clasificacion_imc'] = df['imc'].apply(_clasificar_imc)

    # 12. Clasificar riesgo
    df['riesgo_enfermedad'] = df.apply(_clasificar_riesgo, axis=1)

    stats['registros_limpios'] = len(df)
    logger.info(f"[TRANSFORM] Pipeline completo. Registros limpios: {len(df)}")

    return {'df_clean': df, 'stats': stats}