import logging

logger = logging.getLogger(__name__)


def calcular_imc(peso: float, altura: float) -> float:
    """Calcula el IMC dado peso (kg) y altura (m)."""
    try:
        if altura > 0 and peso > 0:
            return round(peso / (altura ** 2), 2)
    except (ZeroDivisionError, TypeError):
        pass
    return 0.0


def clasificar_imc(imc: float) -> str:
    if imc < 18.5:
        return 'Bajo peso'
    if imc < 25:
        return 'Normal'
    if imc < 30:
        return 'Sobrepeso'
    if imc < 35:
        return 'Obesidad I'
    if imc < 40:
        return 'Obesidad II'
    return 'Obesidad III'


def clasificar_riesgo(data: dict) -> str:
    """
    Clasifica el riesgo clínico de un paciente dado un dict de variables.
    Mismo algoritmo usado en el ETL.
    """
    score = 0

    ps = data.get('presion_sistolica', 0)
    if ps > 180:   score += 4
    elif ps > 160: score += 3
    elif ps > 140: score += 2
    elif ps > 120: score += 1

    gl = data.get('glucosa', 0)
    if gl > 300:   score += 4
    elif gl > 200: score += 3
    elif gl > 126: score += 2
    elif gl > 100: score += 1

    so = data.get('saturacion_oxigeno', 100)
    if so < 85:   score += 4
    elif so < 90: score += 3
    elif so < 94: score += 2

    imc = data.get('imc', 0)
    if imc >= 40:   score += 3
    elif imc >= 35: score += 2
    elif imc >= 30: score += 1
    elif imc < 18.5 and imc > 0: score += 1

    if data.get('fumador'):                 score += 1
    if data.get('consumo_alcohol'):         score += 1
    if data.get('antecedentes_familiares'): score += 1

    edad = data.get('edad', 0)
    if edad > 75:   score += 2
    elif edad > 60: score += 1

    if score >= 8: return 'Crítico'
    if score >= 5: return 'Alto'
    if score >= 2: return 'Medio'
    return 'Bajo'


def enriquecer_paciente(data: dict) -> dict:
    """
    Recibe el dict de datos de un paciente, calcula IMC y riesgo
    y los inyecta antes de guardar.
    """
    peso   = float(data.get('peso', 0) or 0)
    altura = float(data.get('altura', 0) or 0)

    imc = calcular_imc(peso, altura)
    data['imc'] = imc
    data['clasificacion_imc'] = clasificar_imc(imc)
    data['riesgo_enfermedad']  = clasificar_riesgo(data)

    return data