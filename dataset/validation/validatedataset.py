"""
dataset/validate_dataset.py

Utilidad para validar e inspeccionar el dataset clínico fuente
antes de ejecutar el pipeline ETL.

Uso:
    python dataset/validate_dataset.py
    python dataset/validate_dataset.py --path dataset/raw/mi_archivo.xlsx
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Añadir el backend al path para poder importar settings si es necesario
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("[ERROR] pandas y numpy son necesarios. Instala: pip install pandas numpy openpyxl")
    sys.exit(1)


# ──────────────────────────────────────────────
# CONFIGURACIÓN ESPERADA DEL DATASET
# ──────────────────────────────────────────────

EXPECTED_COLUMNS = {
    # Identificación
    "id_paciente":        {"dtype": "object",  "nullable": False},
    "edad":               {"dtype": "numeric", "nullable": False, "min": 0,   "max": 120},
    "genero":             {"dtype": "object",  "nullable": False},
    "peso_kg":            {"dtype": "numeric", "nullable": True,  "min": 1,   "max": 300},
    "talla_cm":           {"dtype": "numeric", "nullable": True,  "min": 30,  "max": 250},
    # Signos vitales
    "presion_sistolica":  {"dtype": "numeric", "nullable": True,  "min": 50,  "max": 300},
    "presion_diastolica": {"dtype": "numeric", "nullable": True,  "min": 20,  "max": 200},
    "frecuencia_cardiaca":{"dtype": "numeric", "nullable": True,  "min": 20,  "max": 300},
    "temperatura":        {"dtype": "numeric", "nullable": True,  "min": 30,  "max": 45},
    "saturacion_o2":      {"dtype": "numeric", "nullable": True,  "min": 50,  "max": 100},
    # Laboratorio
    "glucosa":            {"dtype": "numeric", "nullable": True,  "min": 0,   "max": 1000},
    "hemoglobina":        {"dtype": "numeric", "nullable": True,  "min": 0,   "max": 25},
    "creatinina":         {"dtype": "numeric", "nullable": True,  "min": 0,   "max": 30},
    # Diagnóstico
    "diagnostico":        {"dtype": "object",  "nullable": True},
    "riesgo_clinico":     {"dtype": "object",  "nullable": False},  # target variable
    "fecha_ingreso":      {"dtype": "datetime","nullable": True},
}

MIN_RECORDS = 100
DEFAULT_PATH = BASE_DIR / "dataset" / "raw" / "dataset_clinico.xlsx"


# ──────────────────────────────────────────────
# FUNCIONES DE VALIDACIÓN
# ──────────────────────────────────────────────

def load_dataset(path: Path) -> pd.DataFrame:
    """Carga el dataset desde Excel o CSV."""
    suffix = path.suffix.lower()
    print(f"\n[INFO] Cargando archivo: {path}")

    if suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path, engine="openpyxl")
    elif suffix == ".csv":
        df = pd.read_csv(path)
    else:
        raise ValueError(f"Formato no soportado: {suffix}. Use .xlsx o .csv")

    print(f"[OK]  {len(df):,} registros | {len(df.columns)} columnas cargados.")
    return df


def check_columns(df: pd.DataFrame) -> dict:
    """Verifica columnas presentes vs. esperadas."""
    result = {"status": "ok", "missing": [], "extra": [], "present": []}
    expected = set(EXPECTED_COLUMNS.keys())
    actual = set(df.columns.str.lower().str.strip())

    # Normalizar nombres
    df.columns = df.columns.str.lower().str.strip()

    result["missing"] = sorted(expected - actual)
    result["extra"]   = sorted(actual - expected)
    result["present"] = sorted(expected & actual)

    if result["missing"]:
        result["status"] = "warning"
    return result


def check_nulls(df: pd.DataFrame) -> dict:
    """Analiza valores nulos por columna."""
    result = {}
    for col, rules in EXPECTED_COLUMNS.items():
        if col not in df.columns:
            continue
        null_count = int(df[col].isna().sum())
        null_pct   = round(null_count / len(df) * 100, 2)
        issue = null_count > 0 and not rules.get("nullable", True)
        result[col] = {
            "null_count": null_count,
            "null_pct":   null_pct,
            "issue":      issue,
        }
    return result


def check_ranges(df: pd.DataFrame) -> dict:
    """Verifica rangos válidos para columnas numéricas."""
    result = {}
    for col, rules in EXPECTED_COLUMNS.items():
        if col not in df.columns or rules["dtype"] != "numeric":
            continue
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        out_of_range = 0
        if "min" in rules:
            out_of_range += int((series < rules["min"]).sum())
        if "max" in rules:
            out_of_range += int((series > rules["max"]).sum())
        result[col] = {
            "min_val":      float(series.min()) if len(series) else None,
            "max_val":      float(series.max()) if len(series) else None,
            "mean_val":     round(float(series.mean()), 2) if len(series) else None,
            "out_of_range": out_of_range,
        }
    return result


def check_target(df: pd.DataFrame) -> dict:
    """Analiza la variable objetivo riesgo_clinico."""
    result = {"found": False}
    target_col = "riesgo_clinico"
    if target_col not in df.columns:
        return result

    result["found"] = True
    counts = df[target_col].value_counts().to_dict()
    result["distribution"] = {str(k): int(v) for k, v in counts.items()}
    result["unique_values"] = [str(v) for v in df[target_col].unique().tolist()]
    result["null_count"] = int(df[target_col].isna().sum())
    return result


def check_duplicates(df: pd.DataFrame) -> dict:
    """Detecta registros duplicados."""
    dup_count = int(df.duplicated().sum())
    id_col = "id_paciente" if "id_paciente" in df.columns else None
    id_dups = int(df[id_col].duplicated().sum()) if id_col else None
    return {
        "total_duplicates": dup_count,
        "id_duplicates":    id_dups,
    }


def generate_report(path: Path) -> dict:
    """Genera reporte completo de validación."""
    report = {
        "timestamp":  datetime.now().isoformat(),
        "file":       str(path),
        "file_size_mb": round(path.stat().st_size / 1024 / 1024, 2),
        "overall_status": "ok",
        "sections":   {},
    }

    df = load_dataset(path)
    report["total_records"] = len(df)
    report["total_columns"] = len(df.columns)

    # Registro mínimo
    if len(df) < MIN_RECORDS:
        report["overall_status"] = "error"
        print(f"[ERROR] El dataset tiene solo {len(df)} registros. Mínimo requerido: {MIN_RECORDS}")

    # Columnas
    col_check = check_columns(df)
    report["sections"]["columns"] = col_check
    if col_check["missing"]:
        report["overall_status"] = "warning"
        print(f"[WARN] Columnas faltantes: {col_check['missing']}")
    if col_check["extra"]:
        print(f"[INFO] Columnas adicionales detectadas: {col_check['extra']}")

    # Nulos
    report["sections"]["nulls"] = check_nulls(df)

    # Rangos
    report["sections"]["ranges"] = check_ranges(df)

    # Target
    target_info = check_target(df)
    report["sections"]["target"] = target_info
    if target_info["found"]:
        print(f"[INFO] Distribución de riesgo_clinico: {target_info['distribution']}")

    # Duplicados
    dup_info = check_duplicates(df)
    report["sections"]["duplicates"] = dup_info
    if dup_info["total_duplicates"] > 0:
        print(f"[WARN] {dup_info['total_duplicates']} registros duplicados encontrados.")

    return report


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Validador del Dataset Clínico - HealthAnalytics IPS")
    parser.add_argument("--path", type=str, default=str(DEFAULT_PATH), help="Ruta al archivo Excel o CSV")
    parser.add_argument("--output", type=str, default=None, help="Guardar reporte JSON en esta ruta")
    args = parser.parse_args()

    path = Path(args.path)
    if not path.exists():
        print(f"\n[ERROR] Archivo no encontrado: {path}")
        print(f"        Coloca el dataset en: dataset/raw/dataset_clinico.xlsx")
        sys.exit(1)

    print("\n" + "="*60)
    print("  VALIDACIÓN DE DATASET CLÍNICO - HealthAnalytics IPS")
    print("="*60)

    report = generate_report(path)

    # Mostrar resumen
    print("\n" + "-"*60)
    print("  RESUMEN")
    print("-"*60)
    print(f"  Estado global : {report['overall_status'].upper()}")
    print(f"  Registros     : {report['total_records']:,}")
    print(f"  Columnas      : {report['total_columns']}")
    print(f"  Tamaño        : {report['file_size_mb']} MB")
    print(f"  Timestamp     : {report['timestamp']}")
    print("-"*60)

    # Guardar reporte
    output_path = args.output or str(BASE_DIR / "dataset" / "processed" / "validation_report.json")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n[OK] Reporte guardado en: {output_path}")

    sys.exit(0 if report["overall_status"] == "ok" else 1)


if __name__ == "__main__":
    main()