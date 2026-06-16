from django.db import models 
from django.db import models


class Paciente(models.Model):
    """
    Modelo principal de paciente clínico.
    Las columnas coinciden exactamente con las variables del dataset del reto.
    """

    # ── Identificación ────────────────────────────────────────────────────
    id_paciente = models.AutoField(primary_key=True)
    nombres     = models.CharField(max_length=100)
    apellidos   = models.CharField(max_length=100)
    edad        = models.IntegerField(default=0)
    sexo        = models.CharField(max_length=20, default='Sin datos')

    # ── Antropometría ─────────────────────────────────────────────────────
    peso    = models.FloatField(default=0.0, help_text='kg')
    altura  = models.FloatField(default=0.0, help_text='metros')
    imc     = models.FloatField(default=0.0, help_text='kg/m²')
    clasificacion_imc = models.CharField(max_length=30, blank=True, default='')

    # ── Signos vitales ────────────────────────────────────────────────────
    presion_sistolica   = models.IntegerField(default=0, help_text='mmHg')
    presion_diastolica  = models.IntegerField(default=0, help_text='mmHg')
    frecuencia_cardiaca = models.IntegerField(default=0, help_text='bpm')
    glucosa             = models.FloatField(default=0.0, help_text='mg/dL')
    colesterol          = models.FloatField(default=0.0, help_text='mg/dL')
    saturacion_oxigeno  = models.FloatField(default=0.0, help_text='%')
    temperatura         = models.FloatField(default=0.0, help_text='°C')

    # ── Factores de riesgo ────────────────────────────────────────────────
    antecedentes_familiares = models.BooleanField(default=False)
    fumador                 = models.BooleanField(default=False)
    consumo_alcohol         = models.BooleanField(default=False)
    actividad_fisica        = models.CharField(max_length=50, default='Sin datos')

    # ── Diagnóstico y riesgo ──────────────────────────────────────────────
    diagnostico_preliminar = models.CharField(max_length=200, default='Sin datos')
    riesgo_enfermedad      = models.CharField(
        max_length=20,
        choices=[
            ('Bajo',    'Bajo'),
            ('Medio',   'Medio'),
            ('Alto',    'Alto'),
            ('Crítico', 'Crítico'),
        ],
        default='Bajo',
    )

    # ── Fecha ─────────────────────────────────────────────────────────────
    fecha_consulta = models.DateField(null=True, blank=True)
    creado_en      = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patients_paciente'
        ordering = ['-creado_en']
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'
        indexes = [
            models.Index(fields=['riesgo_enfermedad']),
            models.Index(fields=['fecha_consulta']),
            models.Index(fields=['sexo']),
        ]

    def __str__(self):
        return f"{self.nombres} {self.apellidos} — {self.riesgo_enfermedad}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}".strip()

    @property
    def es_critico(self):
        return (
            self.presion_sistolica > 180 or
            self.glucosa > 300 or
            self.saturacion_oxigeno < 85
        )