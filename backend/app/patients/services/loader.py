import logging
from ..models import Paciente
from .transformer import enriquecer_paciente

logger = logging.getLogger(__name__)


def crear_paciente(data: dict) -> Paciente:
    """
    Enriquece los datos (IMC + riesgo) y crea el paciente en BD.
    """
    data = enriquecer_paciente(data)
    paciente = Paciente.objects.create(**data)
    logger.info(f"[LOADER] Paciente creado: {paciente.nombre_completo} — {paciente.riesgo_enfermedad}")
    return paciente


def actualizar_paciente(paciente: Paciente, data: dict) -> Paciente:
    """
    Actualiza los campos del paciente y recalcula IMC y riesgo.
    """
    data = enriquecer_paciente(data)
    for field, value in data.items():
        if hasattr(paciente, field):
            setattr(paciente, field, value)
    paciente.save()
    logger.info(f"[LOADER] Paciente actualizado: {paciente.nombre_completo}")
    return paciente


def recalcular_todos_los_riesgos() -> int:
    """
    Recalcula el IMC y riesgo de TODOS los pacientes en BD.
    Útil después de cambiar las reglas de clasificación.
    Retorna el número de pacientes actualizados.
    """
    pacientes = Paciente.objects.all()
    count = 0
    for p in pacientes:
        data = {
            'peso': p.peso, 'altura': p.altura,
            'presion_sistolica': p.presion_sistolica,
            'glucosa': p.glucosa,
            'saturacion_oxigeno': p.saturacion_oxigeno,
            'fumador': p.fumador,
            'consumo_alcohol': p.consumo_alcohol,
            'antecedentes_familiares': p.antecedentes_familiares,
            'edad': p.edad,
        }
        data = enriquecer_paciente(data)
        p.imc = data['imc']
        p.clasificacion_imc = data['clasificacion_imc']
        p.riesgo_enfermedad = data['riesgo_enfermedad']
        count += 1

    Paciente.objects.bulk_update(
        pacientes,
        ['imc', 'clasificacion_imc', 'riesgo_enfermedad'],
        batch_size=500,
    )
    logger.info(f"[LOADER] Riesgos recalculados: {count} pacientes")
    return count