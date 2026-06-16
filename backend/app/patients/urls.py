from django.urls import path
from .views import (
    PacienteListView,
    PacienteDetailView,
    PacienteCriticosView,
    RecalcularRiesgosView,
    PacienteStatsView,
)

urlpatterns = [
    # CRUD principal
    path('',                  PacienteListView.as_view(),      name='pacientes-list'),
    path('<int:pk>/',          PacienteDetailView.as_view(),    name='pacientes-detail'),

    # Especiales
    path('criticos/',          PacienteCriticosView.as_view(),  name='pacientes-criticos'),
    path('stats/',             PacienteStatsView.as_view(),     name='pacientes-stats'),
    path('recalcular/',        RecalcularRiesgosView.as_view(), name='pacientes-recalcular'),
]