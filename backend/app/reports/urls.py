"""app.reports — URLs del módulo de reportes.

Este archivo debe exponer `urlpatterns` para que Django pueda incluirlo desde
`config/urls.py`.

A día de hoy, el proyecto ya contiene servicios (generadores) pero no se
incluyeron vistas/endpoint REST; por eso se define un router mínimo.
"""

from django.urls import path

from .views import (
    ReportePacientesView,
    ReporteAnaliticaView,
    ReporteMLView,
    ReporteETLView,
    ReporteHistorialView,
)

urlpatterns = [
    path('pacientes/', ReportePacientesView.as_view(), name='reporte-pacientes'),
    path('analitica/', ReporteAnaliticaView.as_view(), name='reporte-analitica'),
    path('ml/', ReporteMLView.as_view(), name='reporte-ml'),
    path('etl/', ReporteETLView.as_view(), name='reporte-etl'),
    path('historial/', ReporteHistorialView.as_view(), name='reporte-historial'),
]


