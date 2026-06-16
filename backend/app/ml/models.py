from django.db import models

from django.db import models
from django.conf import settings


class AlgoritmoChoices(models.TextChoices):
    LOGISTIC_REGRESSION = 'logistic_regression', 'Regresión Logística'
    RANDOM_FOREST       = 'random_forest',        'Random Forest'
    DECISION_TREE       = 'decision_tree',         'Árbol de Decisión'


class EstadoChoices(models.TextChoices):
    ENTRENANDO = 'ENTRENANDO', 'Entrenando'
    LISTO      = 'LISTO',      'Listo'
    ERROR      = 'ERROR',      'Error'


class MLModel(models.Model):
    """
    Registro de cada modelo ML entrenado.
    El archivo .pkl se guarda en disco; aquí guardamos las métricas.
    """
    nombre      = models.CharField(max_length=100)
    algoritmo   = models.CharField(max_length=30, choices=AlgoritmoChoices.choices)
    version     = models.PositiveIntegerField(default=1)
    estado      = models.CharField(max_length=15, choices=EstadoChoices.choices, default=EstadoChoices.ENTRENANDO)

    # Métricas
    accuracy    = models.FloatField(null=True, blank=True)
    precision   = models.FloatField(null=True, blank=True)
    recall      = models.FloatField(null=True, blank=True)
    f1_score    = models.FloatField(null=True, blank=True)
    roc_auc     = models.FloatField(null=True, blank=True)
    matriz_confusion = models.JSONField(default=dict, blank=True)

    # Meta
    registros_entrenamiento = models.IntegerField(default=0)
    features_usadas         = models.JSONField(default=list, blank=True)
    ruta_archivo            = models.CharField(max_length=255, blank=True)  # path al .pkl
    activo                  = models.BooleanField(default=False)            # modelo en producción
    mensaje_error           = models.TextField(blank=True)

    entrenado_por  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='ml_models'
    )
    creado_en      = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ml_model'
        ordering = ['-creado_en']
        verbose_name = 'Modelo ML'
        verbose_name_plural = 'Modelos ML'

    def __str__(self):
        return f"{self.nombre} v{self.version} ({self.algoritmo}) — {self.estado}"


class Prediction(models.Model):
    """
    Registro de cada predicción realizada por el modelo activo.
    """
    modelo   = models.ForeignKey(MLModel, on_delete=models.SET_NULL, null=True, related_name='predicciones')
    paciente = models.ForeignKey(
        'patients.Paciente', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='predicciones'
    )

    # Entrada y salida
    datos_entrada       = models.JSONField(default=dict)
    riesgo_predicho     = models.CharField(max_length=20)   # Bajo / Medio / Alto / Crítico
    probabilidad        = models.FloatField(null=True, blank=True)  # prob. clase positiva
    probabilidades_dict = models.JSONField(default=dict, blank=True)

    realizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='predicciones'
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ml_prediction'
        ordering = ['-creado_en']
        verbose_name = 'Predicción'
        verbose_name_plural = 'Predicciones'

    def __str__(self):
        return f"Predicción #{self.pk} — {self.riesgo_predicho} ({self.probabilidad:.0%})"