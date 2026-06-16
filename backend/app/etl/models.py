from django.db import models

from django.db import models
from django.conf import settings


class ETLStatus(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    EJECUTANDO = 'EJECUTANDO', 'Ejecutando'
    EXITOSO = 'EXITOSO', 'Exitoso'
    ERROR = 'ERROR', 'Error'


class ETLLog(models.Model):
    """
    Registro de cada ejecución del proceso ETL.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='etl_logs'
    )
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    # Fuente
    archivo_origen = models.CharField(max_length=255, blank=True)
    tipo_origen = models.CharField(
        max_length=10,
        choices=[('excel', 'Excel'), ('csv', 'CSV'), ('auto', 'Automático')],
        default='excel'
    )

    # Contadores
    registros_extraidos = models.IntegerField(default=0)
    registros_limpios = models.IntegerField(default=0)
    duplicados_removidos = models.IntegerField(default=0)
    nulos_tratados = models.IntegerField(default=0)
    outliers_corregidos = models.IntegerField(default=0)
    errores_tipo_corregidos = models.IntegerField(default=0)
    registros_cargados = models.IntegerField(default=0)

    # Estado y tiempo
    tiempo_ejecucion = models.FloatField(default=0.0, help_text='Segundos')
    estado = models.CharField(
        max_length=15,
        choices=ETLStatus.choices,
        default=ETLStatus.PENDIENTE
    )
    mensaje = models.TextField(blank=True)
    detalle_errores = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'etl_log'
        ordering = ['-fecha_inicio']
        verbose_name = 'Log ETL'
        verbose_name_plural = 'Logs ETL'

    def __str__(self):
        return f"ETL #{self.pk} — {self.estado} ({self.fecha_inicio.strftime('%Y-%m-%d %H:%M')})"

    @property
    def duracion_formateada(self):
        t = self.tiempo_ejecucion
        if t < 60:
            return f"{t:.1f}s"
        return f"{t // 60:.0f}m {t % 60:.0f}s"