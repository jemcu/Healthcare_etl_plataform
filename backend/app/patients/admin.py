from django.contrib import admin

from django.contrib import admin
from .models import Paciente


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display  = [
        'id_paciente', 'nombre_completo', 'edad', 'sexo',
        'imc', 'clasificacion_imc', 'presion_sistolica',
        'glucosa', 'saturacion_oxigeno',
        'riesgo_enfermedad', 'diagnostico_preliminar', 'fecha_consulta',
    ]
    list_filter   = ['riesgo_enfermedad', 'sexo', 'fumador', 'clasificacion_imc']
    search_fields = ['nombres', 'apellidos', 'diagnostico_preliminar']
    ordering      = ['-creado_en']
    readonly_fields = ['imc', 'clasificacion_imc', 'riesgo_enfermedad', 'creado_en', 'actualizado_en']

    fieldsets = (
        ('Identificación', {
            'fields': ('nombres', 'apellidos', 'edad', 'sexo', 'fecha_consulta')
        }),
        ('Antropometría', {
            'fields': ('peso', 'altura', 'imc', 'clasificacion_imc')
        }),
        ('Signos Vitales', {
            'fields': (
                'presion_sistolica', 'presion_diastolica', 'frecuencia_cardiaca',
                'glucosa', 'colesterol', 'saturacion_oxigeno', 'temperatura',
            )
        }),
        ('Factores de Riesgo', {
            'fields': ('fumador', 'consumo_alcohol', 'antecedentes_familiares', 'actividad_fisica')
        }),
        ('Diagnóstico y Riesgo', {
            'fields': ('diagnostico_preliminar', 'riesgo_enfermedad')
        }),
        ('Auditoría', {
            'fields': ('creado_en', 'actualizado_en'),
            'classes': ('collapse',),
        }),
    )

    def nombre_completo(self, obj):
        return obj.nombre_completo
    nombre_completo.short_description = 'Nombre'