from django.urls import path
from .views import (
    KPIView,
    DescriptiveStatsView,
    SegmentationView,
    CriticalPatientsView,
    DashboardSummaryView,
    SnapshotView,
)

urlpatterns = [
    # KPIs principales del dashboard
    path('kpis/', KPIView.as_view(), name='analytics-kpis'),

    # Estadísticas descriptivas (media, mediana, moda, desv. std)
    path('stats/', DescriptiveStatsView.as_view(), name='analytics-stats'),

    # Segmentación: ?by=edad|sexo|riesgo|diagnostico|imc
    path('segments/', SegmentationView.as_view(), name='analytics-segments'),

    # Pacientes que superan umbrales críticos
    path('criticos/', CriticalPatientsView.as_view(), name='analytics-criticos'),

    # Resumen completo del dashboard (todas las métricas en 1 request)
    path('dashboard/', DashboardSummaryView.as_view(), name='analytics-dashboard'),

    # Guardar / listar snapshots históricos de KPIs
    path('snapshot/', SnapshotView.as_view(), name='analytics-snapshot'),
]