"""
Excepciones personalizadas para HealthAnalytics IPS.

Todas heredan de HealthAnalyticsBaseError para facilitar
el manejo centralizado de errores en la API.
"""


class HealthAnalyticsBaseError(Exception):
    """
    Excepción base del proyecto.
    Todas las excepciones personalizadas deben heredar de esta clase.
    """

    default_message = "Error en HealthAnalytics IPS."
    default_code = "HEALTHANALYTICS_ERROR"

    def __init__(self, message: str = None, code: str = None, details: dict = None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Serializa la excepción para respuestas JSON de la API."""
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }

    def __repr__(self):
        return f"{self.__class__.__name__}(code={self.code!r}, message={self.message!r})"


# ─── ETL ─────────────────────────────────────────────────────────────────────

class ETLProcessError(HealthAnalyticsBaseError):
    """Error durante el proceso de Extracción, Transformación o Carga."""

    default_message = "Error en el proceso ETL."
    default_code = "ETL_PROCESS_ERROR"


class DataValidationError(HealthAnalyticsBaseError):
    """Error de validación en los datos clínicos del dataset."""

    default_message = "Los datos clínicos no superaron la validación."
    default_code = "DATA_VALIDATION_ERROR"


# ─── Machine Learning ─────────────────────────────────────────────────────────

class MLModelError(HealthAnalyticsBaseError):
    """Error relacionado con el entrenamiento o predicción de modelos ML."""

    default_message = "Error en el modelo de Machine Learning."
    default_code = "ML_MODEL_ERROR"


class ModelNotTrainedError(MLModelError):
    """Se intentó usar un modelo que no ha sido entrenado."""

    default_message = "El modelo solicitado no ha sido entrenado todavía."
    default_code = "MODEL_NOT_TRAINED"


# ─── Pacientes ────────────────────────────────────────────────────────────────

class PatientNotFoundError(HealthAnalyticsBaseError):
    """El paciente buscado no existe en la base de datos."""

    default_message = "Paciente no encontrado."
    default_code = "PATIENT_NOT_FOUND"


class DuplicatePatientError(HealthAnalyticsBaseError):
    """Se intentó registrar un paciente con un identificador ya existente."""

    default_message = "Ya existe un paciente con ese identificador."
    default_code = "DUPLICATE_PATIENT"


# ─── Reportes ─────────────────────────────────────────────────────────────────

class ReportGenerationError(HealthAnalyticsBaseError):
    """Error durante la generación de reportes (PDF, Excel, CSV)."""

    default_message = "No se pudo generar el reporte."
    default_code = "REPORT_GENERATION_ERROR"


# ─── Autenticación y Permisos ─────────────────────────────────────────────────

class AuthenticationError(HealthAnalyticsBaseError):
    """Fallo de autenticación: credenciales inválidas o token expirado."""

    default_message = "Autenticación fallida. Verifique sus credenciales."
    default_code = "AUTHENTICATION_FAILED"


class PermissionDeniedError(HealthAnalyticsBaseError):
    """El usuario no tiene permisos para realizar esta acción."""

    default_message = "No tiene permisos para ejecutar esta acción."
    default_code = "PERMISSION_DENIED"