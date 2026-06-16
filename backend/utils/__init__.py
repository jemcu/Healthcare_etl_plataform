"""
utils — Utilidades transversales para HealthAnalytics IPS.
"""

from .exceptions import (
    HealthAnalyticsBaseError,
    ETLProcessError,
    DataValidationError,
    MLModelError,
    PatientNotFoundError,
    ReportGenerationError,
    AuthenticationError,
    PermissionDeniedError,
)
from .pagination import StandardPagination, LargePagination
from .validators import (
    validate_imc,
    validate_age,
    validate_glucose,
    validate_blood_pressure,
    validate_patient_data,
    sanitize_string,
)

__all__ = [
    # Exceptions
    "HealthAnalyticsBaseError",
    "ETLProcessError",
    "DataValidationError",
    "MLModelError",
    "PatientNotFoundError",
    "ReportGenerationError",
    "AuthenticationError",
    "PermissionDeniedError",
    # Pagination
    "StandardPagination",
    "LargePagination",
    # Validators
    "validate_imc",
    "validate_age",
    "validate_glucose",
    "validate_blood_pressure",
    "validate_patient_data",
    "sanitize_string",
]