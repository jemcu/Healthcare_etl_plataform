from django.contrib import admin

from django.contrib import admin
from .models import ReporteLog


@admin.register(ReporteLog)
class ReporteLogAdmin(admin.ModelAdmin):
    list_display  = ['id', 'tipo', 'formato', 'filas', 'generado_por', 'creado_en']
    list_filter   = ['tipo', 'formato', 'creado_en']
    search_fields = ['generado_por__username']
    readonly_fields = ['creado_en', 'filtros']
    ordering = ['-creado_en']