from django.db.models import Count, Avg, Q
from django.apps import apps


def get_paciente_model():
    return apps.get_model('patients', 'Paciente')


def calcular_kpis():
    """
    Calcula los KPIs médicos principales del dashboard.
    """
    Paciente = get_paciente_model()
    qs = Paciente.objects.all()
    total = qs.count()

    if total == 0:
        return {'total_pacientes': 0}

    # ── Distribución por nivel de riesgo ──────────────────────────────────
    riesgo_dist = (
        qs.values('riesgo_enfermedad')
          .annotate(cantidad=Count('id_paciente'))
          .order_by('riesgo_enfermedad')
    )
    riesgo_map = {r['riesgo_enfermedad']: r['cantidad'] for r in riesgo_dist}

    # ── Pacientes críticos (criterios clínicos) ───────────────────────────
    criticos = qs.filter(
        Q(presion_sistolica__gt=180) |
        Q(glucosa__gt=300) |
        Q(saturacion_oxigeno__lt=85)
    ).count()

    # ── Pacientes hipertensos ─────────────────────────────────────────────
    hipertensos = qs.filter(presion_sistolica__gte=140).count()

    # ── Pacientes diabéticos (glucosa en ayunas >= 126 mg/dL) ────────────
    diabeticos = qs.filter(glucosa__gte=126).count()

    # ── Fumadores ─────────────────────────────────────────────────────────
    fumadores = qs.filter(fumador=True).count()

    # ── Distribución por IMC ──────────────────────────────────────────────
    bajo_peso   = qs.filter(imc__lt=18.5).count()
    normal      = qs.filter(imc__gte=18.5, imc__lt=25).count()
    sobrepeso   = qs.filter(imc__gte=25, imc__lt=30).count()
    obesidad    = qs.filter(imc__gte=30).count()

    # ── Promedios generales ───────────────────────────────────────────────
    promedios = qs.aggregate(
        avg_edad=Avg('edad'),
        avg_imc=Avg('imc'),
        avg_glucosa=Avg('glucosa'),
        avg_colesterol=Avg('colesterol'),
        avg_presion_sistolica=Avg('presion_sistolica'),
        avg_frecuencia_cardiaca=Avg('frecuencia_cardiaca'),
    )

    return {
        'total_pacientes': total,
        'distribucion_riesgo': {
            'bajo': riesgo_map.get('Bajo', 0),
            'medio': riesgo_map.get('Medio', 0),
            'alto': riesgo_map.get('Alto', 0),
            'critico': riesgo_map.get('Crítico', 0),
        },
        'pacientes_criticos': criticos,
        'pacientes_hipertensos': hipertensos,
        'porcentaje_hipertensos': round((hipertensos / total) * 100, 1),
        'pacientes_diabeticos': diabeticos,
        'porcentaje_diabeticos': round((diabeticos / total) * 100, 1),
        'pacientes_fumadores': fumadores,
        'porcentaje_fumadores': round((fumadores / total) * 100, 1),
        'distribucion_imc': {
            'bajo_peso': bajo_peso,
            'normal': normal,
            'sobrepeso': sobrepeso,
            'obesidad': obesidad,
        },
        'promedios': {
            'edad': round(promedios['avg_edad'] or 0, 1),
            'imc': round(promedios['avg_imc'] or 0, 2),
            'glucosa': round(promedios['avg_glucosa'] or 0, 1),
            'colesterol': round(promedios['avg_colesterol'] or 0, 1),
            'presion_sistolica': round(promedios['avg_presion_sistolica'] or 0, 1),
            'frecuencia_cardiaca': round(promedios['avg_frecuencia_cardiaca'] or 0, 1),
        },
    }