"""
HealthAnalytics IPS — URLs raíz
Registra todas las rutas de los módulos del backend.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [

    # ── Admin Django ──────────────────────────────────────────────────────
    path('admin/', admin.site.urls),

    # ── Autenticación y usuarios ──────────────────────────────────────────
    path('api/auth/',       include('app.authentication.Urls')),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # ── Pacientes ─────────────────────────────────────────────────────────
    path('api/pacientes/',  include('app.patients.urls')),

    # ── ETL ───────────────────────────────────────────────────────────────
    path('api/etl/',        include('app.etl.Urls')),


    # ── Analítica ─────────────────────────────────────────────────────────
    path('api/analytics/',  include('app.analytics.urls')),

    # ── Machine Learning ──────────────────────────────────────────────────
    path('api/ml/',         include('app.ml.urls')),

    # ── Reportes ──────────────────────────────────────────────────────────
    path('api/reportes/',   include('app.reports.urls')),

    # ── Dashboard ─────────────────────────────────────────────────────────
    path('api/dashboard/',  include('app.dashboard.urls')),

    # ── Swagger / OpenAPI ─────────────────────────────────────────────────
    path('api/schema/',     SpectacularAPIView.as_view(),        name='schema'),
    path('api/docs/',       SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/',      SpectacularRedocView.as_view(url_name='schema'),   name='redoc'),

]

# ── Servir media en desarrollo ────────────────────────────────────────────────
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)