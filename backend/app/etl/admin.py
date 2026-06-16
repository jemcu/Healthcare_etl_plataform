from django.contrib import admin

from django.contrib import admin
from .models import ETLLog


@admin.register(ETLLog)
class ETLLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'archivo_origen', 'tipo_origen', 'estado',
        'registros_extraidos', 'registros_limpios', 'registros_cargados',
        'duracion_formateada', 'usuario', 'fecha_inicio'
    ]
    list_filter = ['estado', 'tipo_origen', 'fecha_inicio']
    search_fields = ['archivo_origen', 'mensaje']
    readonly_fields = [
        'fecha_inicio', 'fecha_fin', 'tiempo_ejecucion',
        'registros_extraidos', 'registros_limpios', 'registros_cargados',
        'duplicados_removidos', 'nulos_tratados',
        'outliers_corregidos', 'errores_tipo_corregidos',
        'detalle_errores',
    ]
    ordering = ['-fecha_inicio']