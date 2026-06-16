from django.urls import path
from .views import (
    DashboardSummaryView,
    DashboardKPIsView,
    DashboardChartsView,
    DashboardETLStatusView,
    DashboardMLStatusView,
)

urlpatterns = [
    # Resumen completo (todas las secciones en 1 request)
    path('',            DashboardSummaryView.as_view(),  name='dashboard-summary'),

    # KPIs clínicos rápidos
    path('kpis/',       DashboardKPIsView.as_view(),     name='dashboard-kpis'),

    # Datos para gráficas Chart.js
    path('charts/',     DashboardChartsView.as_view(),   name='dashboard-charts'),

    # Estado del último ETL
    path('etl-status/', DashboardETLStatusView.as_view(), name='dashboard-etl-status'),

    # Estado del modelo ML activo
    path('ml-status/',  DashboardMLStatusView.as_view(),  name='dashboard-ml-status'),
]