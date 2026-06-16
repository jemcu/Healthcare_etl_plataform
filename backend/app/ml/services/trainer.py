import os
import pickle
import logging
from datetime import datetime

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from django.conf import settings

from .preprocessor import load_dataset_from_db, preprocess, FEATURE_COLUMNS


logger = logging.getLogger(__name__)

# Directorio donde se guardan los modelos .pkl (definido en settings)
MODELS_DIR = str(settings.ML_MODELS_DIR)
os.makedirs(MODELS_DIR, exist_ok=True)



ALGORITMOS = {
    'logistic_regression': LogisticRegression(
        max_iter=1000,
        # sklearn >= 1.5 ya no acepta `multi_class` en LogisticRegression
        solver='lbfgs',
        random_state=42,
    ),

    'random_forest': RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1,
    ),
    'decision_tree': DecisionTreeClassifier(
        max_depth=8,
        random_state=42,
    ),
}


def train_model(algoritmo: str = 'random_forest', ml_model_instance=None) -> dict:
    """
    Entrena el modelo seleccionado con los datos actuales de la BD.
    Guarda el pipeline (.pkl) en disco.
    Retorna dict con métricas y ruta del archivo.
    """
    if algoritmo not in ALGORITMOS:
        raise ValueError(f"Algoritmo '{algoritmo}' no válido. Opciones: {list(ALGORITMOS.keys())}")

    logger.info(f"[TRAIN] Iniciando entrenamiento: {algoritmo}")
    start = datetime.now()

    # 1. Cargar y preprocesar
    df = load_dataset_from_db()
    if len(df) < 50:
        raise ValueError("Se necesitan al menos 50 registros en BD para entrenar. Ejecuta el ETL primero.")

    prep = preprocess(df)
    X, y = prep['X'], prep['y']

    # 2. Split train/test (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 3. Construir pipeline (scaler + modelo)
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('model', ALGORITMOS[algoritmo]),
    ])

    # 4. Entrenar
    pipeline.fit(X_train, y_train)
    logger.info(f"[TRAIN] Entrenamiento completado en {(datetime.now()-start).total_seconds():.1f}s")

    # 5. Guardar en disco
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{algoritmo}_{timestamp}.pkl"
    filepath = os.path.join(MODELS_DIR, filename)

    with open(filepath, 'wb') as f:
        pickle.dump({
            'pipeline': pipeline,
            'feature_names': FEATURE_COLUMNS,
            'algoritmo': algoritmo,
            'trained_at': timestamp,
        }, f)

    logger.info(f"[TRAIN] Modelo guardado: {filepath}")

    elapsed = (datetime.now() - start).total_seconds()

    return {
        'pipeline': pipeline,
        'X_test': X_test,
        'y_test': y_test,
        'ruta_archivo': filepath,
        'registros_entrenamiento': len(X_train),
        'registros_prueba': len(X_test),
        'tiempo_entrenamiento': round(elapsed, 2),
        'distribucion_clases': prep['distribucion'],
        'feature_names': FEATURE_COLUMNS,
    }


def load_active_model() -> dict | None:
    """
    Carga el modelo activo (.pkl) desde disco.
    Retorna el dict guardado o None si no existe.
    """
    from django.apps import apps
    from app.ml.models import EstadoChoices

    MLModel = apps.get_model('ml', 'MLModel')

    modelo_activo = MLModel.objects.filter(activo=True, estado=EstadoChoices.LISTO).first()
    if not modelo_activo or not modelo_activo.ruta_archivo:
        return None

    if not os.path.exists(modelo_activo.ruta_archivo):
        logger.warning(f"[LOAD] Archivo no encontrado: {modelo_activo.ruta_archivo}")
        return None

    with open(modelo_activo.ruta_archivo, 'rb') as f:
        data = pickle.load(f)

    data['ml_model_instance'] = modelo_activo
    return data