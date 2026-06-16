import logging
import numpy as np
from .preprocessor import preprocess_single, RIESGO_ENCODING
from .trainer import load_active_model

logger = logging.getLogger(__name__)

# Decodificador inverso
RIESGO_DECODING = {v: k for k, v in RIESGO_ENCODING.items()}


def predecir_riesgo(datos_paciente: dict) -> dict:
    """
    Recibe un dict con las variables clínicas del paciente y retorna
    la predicción de riesgo usando el modelo activo.

    Retorna:
    {
        'riesgo_predicho': 'Alto',
        'probabilidad':    0.78,
        'probabilidades':  { 'Bajo': 0.05, 'Medio': 0.12, 'Alto': 0.78, 'Crítico': 0.05 },
        'modelo_usado':    'Random Forest v2',
    }
    """
    modelo_data = load_active_model()
    if not modelo_data:
        raise ValueError(
            "No hay ningún modelo activo. Ve a POST /api/ml/train/ para entrenar uno primero."
        )

    pipeline      = modelo_data['pipeline']
    ml_instance   = modelo_data.get('ml_model_instance')

    # Preprocesar entrada
    X = preprocess_single(datos_paciente)

    # Predicción
    y_pred = pipeline.predict(X)[0]
    riesgo = RIESGO_DECODING.get(int(y_pred), 'Sin datos')

    # Probabilidades por clase
    probabilidades = {}
    prob_principal = None
    try:
        y_proba = pipeline.predict_proba(X)[0]
        clases_modelo = pipeline.classes_
        for idx, clase in enumerate(clases_modelo):
            label = RIESGO_DECODING.get(int(clase), str(clase))
            probabilidades[label] = round(float(y_proba[idx]), 4)
        prob_principal = probabilidades.get(riesgo)
    except Exception:
        pass

    logger.info(f"[PREDICT] Riesgo predicho: {riesgo} (prob={prob_principal})")

    return {
        'riesgo_predicho':  riesgo,
        'probabilidad':     prob_principal,
        'probabilidades':   probabilidades,
        'modelo_usado':     str(ml_instance) if ml_instance else modelo_data.get('algoritmo', ''),
    }


def predecir_batch(lista_pacientes: list) -> list:
    """
    Predice el riesgo para una lista de pacientes.
    """
    return [predecir_riesgo(p) for p in lista_pacientes]