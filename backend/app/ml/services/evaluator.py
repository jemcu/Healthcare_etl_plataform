import numpy as np
import logging
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, roc_auc_score,
    classification_report,
)

logger = logging.getLogger(__name__)

RIESGO_LABELS = ['Bajo', 'Medio', 'Alto', 'Crítico']


def evaluar_modelo(pipeline, X_test: np.ndarray, y_test: np.ndarray) -> dict:
    """
    Calcula todas las métricas obligatorias del reto:
    Accuracy, Precision, Recall, F1-Score, Matriz de confusión, ROC AUC.
    """
    y_pred = pipeline.predict(X_test)

    # Clases presentes en y_test
    clases = sorted(np.unique(np.concatenate([y_test, y_pred])))
    labels_presentes = [RIESGO_LABELS[c] for c in clases if c < len(RIESGO_LABELS)]

    # Métricas globales (weighted para multiclase)
    accuracy  = float(accuracy_score(y_test, y_pred))
    precision = float(precision_score(y_test, y_pred, average='weighted', zero_division=0))
    recall    = float(recall_score(y_test, y_pred, average='weighted', zero_division=0))
    f1        = float(f1_score(y_test, y_pred, average='weighted', zero_division=0))

    # ROC AUC (solo si el modelo soporta predict_proba)
    roc_auc = None
    try:
        y_proba = pipeline.predict_proba(X_test)
        if y_proba.shape[1] == 2:
            roc_auc = float(roc_auc_score(y_test, y_proba[:, 1]))
        else:
            roc_auc = float(roc_auc_score(y_test, y_proba, multi_class='ovr', average='weighted'))
    except Exception:
        pass

    # Matriz de confusión
    cm = confusion_matrix(y_test, y_pred, labels=clases)

    # Reporte por clase
    report = classification_report(
        y_test, y_pred,
        labels=clases,
        target_names=labels_presentes,
        output_dict=True,
        zero_division=0,
    )

    metricas = {
        'accuracy':  round(accuracy, 4),
        'precision': round(precision, 4),
        'recall':    round(recall, 4),
        'f1_score':  round(f1, 4),
        'roc_auc':   round(roc_auc, 4) if roc_auc is not None else None,
        'matriz_confusion': {
            'labels': labels_presentes,
            'matrix': cm.tolist(),
        },
        'reporte_por_clase': report,
        'total_test': int(len(y_test)),
        'correctas':  int((y_test == y_pred).sum()),
        'incorrectas': int((y_test != y_pred).sum()),
    }

    logger.info(
        f"[EVAL] Accuracy={accuracy:.4f} | Precision={precision:.4f} | "
        f"Recall={recall:.4f} | F1={f1:.4f}"
    )

    return metricas