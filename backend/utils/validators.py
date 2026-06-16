"""
Validadores de datos clínicos para HealthAnalytics IPS.

Funciones puras de validación usadas tanto en el pipeline ETL
como en los serializers de DRF para garantizar integridad de datos.
"""

import re
from typing import Any, Dict, List, Tuple

from .exceptions import DataValidationError


# ─── Rangos clínicos de referencia ───────────────────────────────────────────

CLINICAL_RANGES = {
    "imc":             (10.0, 70.0),   # kg/m²
    "age":             (0,    120),    # años
    "glucose":         (50,   600),    # mg/dL
    "systolic_bp":     (60,   250),    # mmHg
    "diastolic_bp":    (40,   150),    # mmHg
    "cholesterol":     (50,   600),    # mg/dL
    "triglycerides":   (30,   1000),   # mg/dL
}


# ─── Validadores individuales ─────────────────────────────────────────────────

def validate_imc(value: float) -> float:
    """
    Valida el Índice de Masa Corporal (IMC).

    Args:
        value: Valor numérico del IMC.

    Returns:
        El mismo valor si es válido.

    Raises:
        DataValidationError: Si está fuera del rango clínico aceptable.
    """
    min_val, max_val = CLINICAL_RANGES["imc"]
    _assert_in_range(value, min_val, max_val, field="IMC", unit="kg/m²")
    return float(value)


def validate_age(value: int) -> int:
    """Valida la edad del paciente (0–120 años)."""
    min_val, max_val = CLINICAL_RANGES["age"]
    _assert_in_range(value, min_val, max_val, field="Edad", unit="años")
    return int(value)


def validate_glucose(value: float) -> float:
    """Valida la glucemia en sangre (50–600 mg/dL)."""
    min_val, max_val = CLINICAL_RANGES["glucose"]
    _assert_in_range(value, min_val, max_val, field="Glucosa", unit="mg/dL")
    return float(value)


def validate_blood_pressure(systolic: float, diastolic: float) -> Tuple[float, float]:
    """
    Valida la presión arterial sistólica y diastólica.

    Raises:
        DataValidationError: Si los valores están fuera de rango
                             o si diastólica ≥ sistólica.
    """
    s_min, s_max = CLINICAL_RANGES["systolic_bp"]
    d_min, d_max = CLINICAL_RANGES["diastolic_bp"]

    _assert_in_range(systolic,  s_min, s_max, field="Presión sistólica",  unit="mmHg")
    _assert_in_range(diastolic, d_min, d_max, field="Presión diastólica", unit="mmHg")

    if diastolic >= systolic:
        raise DataValidationError(
            message=(
                f"La presión diastólica ({diastolic} mmHg) debe ser menor "
                f"que la sistólica ({systolic} mmHg)."
            ),
            details={"systolic": systolic, "diastolic": diastolic},
        )

    return float(systolic), float(diastolic)


# ─── Validador de registro completo ──────────────────────────────────────────

def validate_patient_data(data: Dict[str, Any]) -> Dict[str, List[str]]:
    """
    Valida un registro completo de paciente.

    Args:
        data: Diccionario con los campos del paciente.

    Returns:
        Diccionario {campo: [errores]} — vacío si todo es válido.
    """
    errors: Dict[str, List[str]] = {}

    def _collect(field: str, validator, *args):
        try:
            validator(*args)
        except DataValidationError as exc:
            errors.setdefault(field, []).append(exc.message)
        except (TypeError, ValueError) as exc:
            errors.setdefault(field, []).append(
                f"Valor inválido para {field}: {exc}"
            )

    # Edad
    if "age" in data:
        _collect("age", validate_age, data["age"])

    # IMC
    if "imc" in data:
        _collect("imc", validate_imc, data["imc"])

    # Glucosa
    if "glucose" in data:
        _collect("glucose", validate_glucose, data["glucose"])

    # Presión arterial
    if "systolic_bp" in data and "diastolic_bp" in data:
        _collect(
            "blood_pressure",
            validate_blood_pressure,
            data["systolic_bp"],
            data["diastolic_bp"],
        )

    # Nombre / texto
    if "name" in data:
        cleaned = sanitize_string(data["name"])
        if len(cleaned) < 2:
            errors.setdefault("name", []).append(
                "El nombre debe tener al menos 2 caracteres."
            )

    return errors


# ─── Utilidades de texto ──────────────────────────────────────────────────────

def sanitize_string(value: str) -> str:
    """
    Limpia una cadena de texto eliminando caracteres no permitidos.

    - Elimina espacios al inicio/final.
    - Colapsa múltiples espacios internos en uno solo.
    - Elimina caracteres de control.

    Args:
        value: Cadena de texto a limpiar.

    Returns:
        Cadena sanitizada.
    """
    if not isinstance(value, str):
        raise DataValidationError(
            message=f"Se esperaba una cadena de texto, se recibió: {type(value).__name__}",
            code="INVALID_STRING_TYPE",
        )
    # Eliminar caracteres de control (excepto saltos de línea estándar)
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value)
    # Colapsar espacios múltiples
    value = re.sub(r" {2,}", " ", value)
    return value.strip()


# ─── Helper interno ───────────────────────────────────────────────────────────

def _assert_in_range(
    value: Any, min_val: float, max_val: float, field: str, unit: str = ""
) -> None:
    """Lanza DataValidationError si el valor está fuera del rango esperado."""
    try:
        num = float(value)
    except (TypeError, ValueError):
        raise DataValidationError(
            message=f"El campo '{field}' debe ser numérico. Valor recibido: {value!r}",
            code="INVALID_NUMERIC_VALUE",
            details={"field": field, "value": value},
        )

    if not (min_val <= num <= max_val):
        raise DataValidationError(
            message=(
                f"{field} fuera de rango: {num} {unit}. "
                f"Rango clínico aceptado: [{min_val}, {max_val}] {unit}."
            ),
            code="OUT_OF_RANGE",
            details={"field": field, "value": num, "min": min_val, "max": max_val},
        )