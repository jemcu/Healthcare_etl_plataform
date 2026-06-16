from django.db.models import Count, Avg
from django.apps import apps


def get_paciente_model():
    return apps.get_model('patients', 'Paciente')


def segmentar_por_edad():
    """
    Agrupa pacientes en rangos de edad clínicos.
    """
    Paciente = get_paciente_model()
    qs = Paciente.objects.all()

    rangos = {
        '0-17 (Pediátrico)': qs.filter(edad__lt=18).count(),
        '18-35 (Adulto joven)': qs.filter(edad__gte=18, edad__lte=35).count(),
        '36-60 (Adulto)': qs.filter(edad__gte=36, edad__lte=60).count(),
        '61-80 (Adulto mayor)': qs.filter(edad__gte=61, edad__lte=80).count(),
        '80+ (Longevo)': qs.filter(edad__gt=80).count(),
    }
    return rangos


def segmentar_por_sexo():
    Paciente = get_paciente_model()
    result = (
        Paciente.objects
        .values('sexo')
        .annotate(cantidad=Count('id_paciente'), promedio_imc=Avg('imc'))
        .order_by('sexo')
    )
    return list(result)


def segmentar_por_riesgo():
    Paciente = get_paciente_model()
    result = (
        Paciente.objects
        .values('riesgo_enfermedad')
        .annotate(
            cantidad=Count('id_paciente'),
            promedio_edad=Avg('edad'),
            promedio_glucosa=Avg('glucosa'),
            promedio_presion=Avg('presion_sistolica'),
        )
        .order_by('riesgo_enfermedad')
    )
    return list(result)


def segmentar_por_diagnostico():
    Paciente = get_paciente_model()
    result = (
        Paciente.objects
        .values('diagnostico_preliminar')
        .annotate(cantidad=Count('id_paciente'))
        .order_by('-cantidad')[:10]  # Top 10 diagnósticos
    )
    return list(result)


def segmentar_por_imc():
    Paciente = get_paciente_model()
    qs = Paciente.objects.all()
    return {
        'bajo_peso': qs.filter(imc__lt=18.5).count(),
        'normal': qs.filter(imc__gte=18.5, imc__lt=25).count(),
        'sobrepeso': qs.filter(imc__gte=25, imc__lt=30).count(),
        'obesidad_I': qs.filter(imc__gte=30, imc__lt=35).count(),
        'obesidad_II': qs.filter(imc__gte=35, imc__lt=40).count(),
        'obesidad_III': qs.filter(imc__gte=40).count(),
    }


def obtener_pacientes_criticos():
    """
    Retorna lista de pacientes que superan umbrales críticos.
    """
    from django.db.models import Q
    Paciente = get_paciente_model()

    criticos = Paciente.objects.filter(
        Q(presion_sistolica__gt=180) |
        Q(glucosa__gt=300) |
        Q(saturacion_oxigeno__lt=85)
    ).values(
        'id_paciente', 'nombres', 'apellidos', 'edad',
        'presion_sistolica', 'glucosa', 'saturacion_oxigeno',
        'riesgo_enfermedad', 'diagnostico_preliminar'
    ).order_by('-presion_sistolica')[:50]

    return list(criticos)