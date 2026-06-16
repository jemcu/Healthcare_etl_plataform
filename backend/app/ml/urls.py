from django.urls import path
from .views import (
    TrainModelView,
    ModelListView,
    ModelDetailView,
    PredictView,
    MetricsView,
    PredictionHistoryView,
)

urlpatterns = [
    # Entrenamiento
    path('train/',              TrainModelView.as_view(),       name='ml-train'),

    # Modelos entrenados
    path('models/',             ModelListView.as_view(),         name='ml-models-list'),
    path('models/<int:pk>/',    ModelDetailView.as_view(),       name='ml-models-detail'),

    # Predicción individual
    path('predict/',            PredictView.as_view(),           name='ml-predict'),

    # Métricas del modelo activo
    path('metrics/',            MetricsView.as_view(),           name='ml-metrics'),

    # Historial de predicciones
    path('predictions/',        PredictionHistoryView.as_view(), name='ml-predictions'),
]