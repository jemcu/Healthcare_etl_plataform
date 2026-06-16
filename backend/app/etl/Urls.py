from django.urls import path
from .views import (
    RunETLView,
    UploadAndRunETLView,
    ETLHistoryView,
    ETLLogDetailView,
    ETLStatusView,
)

urlpatterns = [
    # Ejecutar ETL sobre dataset por defecto
    path('run/',              RunETLView.as_view(),        name='etl-run'),

    # Subir archivo y ejecutar ETL
    path('upload/',           UploadAndRunETLView.as_view(), name='etl-upload'),

    # Historial de ejecuciones
    path('history/',          ETLHistoryView.as_view(),    name='etl-history'),
    path('history/<int:pk>/', ETLLogDetailView.as_view(),  name='etl-history-detail'),

    # Estado del último proceso
    path('status/',           ETLStatusView.as_view(),     name='etl-status'),
]

