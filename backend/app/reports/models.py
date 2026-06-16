from django.db import models

from django.db import models
from django.conf import settings


class FormatoChoices(models.TextChoices):
    PDF   = 'pdf',   'PDF'
    EXCEL = 'excel', 'Excel'
    CSV   = 'csv',   'CSV'


class ReporteTipo(models.TextChoices):
    PACIENTES  = 'pacientes',  'Reporte de Pacientes'
    ETL        = 'etl',        'Reporte ETL'
    ANALITICA  = 'analitica',  'Reporte Analítica'
    ML         = 'ml',         'Reporte Machine Learning'
    CRITICOS   = 'criticos',   'Reporte Pacientes Críticos'


class ReporteLog(models.Model):
    """
    Registra cada reporte generado: quién lo pidió, qué tipo, cuándo.
    """
    tipo      = models.CharField(max_length=20, choices=ReporteTipo.choices)
    formato   = models.CharField(max_length=10, choices=FormatoChoices.choices)
    filtros   = models.JSONField(default=dict, blank=True)   # params usados
    filas     = models.IntegerField(default=0)
    generado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, null=True, blank=True,
        related_name='reportes'
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reports_log'
        ordering = ['-creado_en']
        verbose_name = 'Log de Reporte'
        verbose_name_plural = 'Logs de Reportes'

    def __str__(self):
        return f"{self.tipo} ({self.formato}) — {self.creado_en.strftime('%Y-%m-%d %H:%M')}"