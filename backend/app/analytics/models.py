from django.db import models

from django.db import models


class ClinicalSnapshot(models.Model):
    """
    Snapshot de métricas clínicas calculadas en un momento dado.
    Permite guardar histórico de KPIs para comparar tendencias.
    """
    fecha_calculo = models.DateTimeField(auto_now_add=True)
    total_pacientes = models.IntegerField(default=0)
    pacientes_criticos = models.IntegerField(default=0)
    pacientes_alto_riesgo = models.IntegerField(default=0)
    pacientes_medio_riesgo = models.IntegerField(default=0)
    pacientes_bajo_riesgo = models.IntegerField(default=0)
    pacientes_hipertensos = models.IntegerField(default=0)
    pacientes_diabeticos = models.IntegerField(default=0)
    pacientes_fumadores = models.IntegerField(default=0)
    promedio_edad = models.FloatField(default=0.0)
    promedio_imc = models.FloatField(default=0.0)
    promedio_glucosa = models.FloatField(default=0.0)
    promedio_colesterol = models.FloatField(default=0.0)
    promedio_presion_sistolica = models.FloatField(default=0.0)

    class Meta:
        db_table = 'analytics_clinical_snapshot'
        ordering = ['-fecha_calculo']
        verbose_name = 'Snapshot Clínico'
        verbose_name_plural = 'Snapshots Clínicos'

    def __str__(self):
        return f"Snapshot {self.fecha_calculo.strftime('%Y-%m-%d %H:%M')}"