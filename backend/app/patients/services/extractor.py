import pandas as pd
import logging
from django.db.models import QuerySet
from ..models import Paciente

logger = logging.getLogger(__name__)


def get_pacientes_queryset(
    riesgo: str = None,
    sexo: str = None,
    edad_min: int = None,
    edad_max: int = None,
    diagnostico: str = None,
    criticos_only: bool = False,
) -> QuerySet:
    """
    Devuelve un QuerySet filtrado de pacientes según los parámetros recibidos.
    """
    qs = Paciente.objects.all()

    if riesgo:
        qs = qs.filter(riesgo_enfermedad__iexact=riesgo)
    if sexo:
        qs = qs.filter(sexo__iexact=sexo)
    if edad_min is not None:
        qs = qs.filter(edad__gte=edad_min)
    if edad_max is not None:
        qs = qs.filter(edad__lte=edad_max)
    if diagnostico:
        qs = qs.filter(diagnostico_preliminar__icontains=diagnostico)
    if criticos_only:
        from django.db.models import Q
        qs = qs.filter(
            Q(presion_sistolica__gt=180) |
            Q(glucosa__gt=300) |
            Q(saturacion_oxigeno__lt=85)
        )
    return qs


def pacientes_to_dataframe(qs: QuerySet = None) -> pd.DataFrame:
    """
    Exporta el QuerySet de pacientes a un DataFrame de Pandas.
    Útil para análisis internos y generación de reportes.
    """
    if qs is None:
        qs = Paciente.objects.all()

    values = list(qs.values(
        'id_paciente', 'nombres', 'apellidos', 'edad', 'sexo',
        'peso', 'altura', 'imc', 'clasificacion_imc',
        'presion_sistolica', 'presion_diastolica', 'frecuencia_cardiaca',
        'glucosa', 'colesterol', 'saturacion_oxigeno', 'temperatura',
        'antecedentes_familiares', 'fumador', 'consumo_alcohol',
        'actividad_fisica', 'diagnostico_preliminar',
        'riesgo_enfermedad', 'fecha_consulta',
    ))

    df = pd.DataFrame(values)
    logger.info(f"[EXTRACTOR] DataFrame exportado: {len(df)} registros")
    return df