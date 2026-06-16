from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    LoginView,
    LogoutView,
    MeView,
    RegisterView,
    UserListView,
    UserDetailView,
    ChangePasswordView,
)

urlpatterns = [
    # ── Sesión ────────────────────────────────────────────────────────────
    path('login/',           LoginView.as_view(),         name='auth-login'),
    path('logout/',          LogoutView.as_view(),         name='auth-logout'),
    path('token/refresh/',   TokenRefreshView.as_view(),   name='auth-token-refresh'),

    # ── Usuario autenticado ───────────────────────────────────────────────
    path('me/',              MeView.as_view(),             name='auth-me'),
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),

    # ── Gestión de usuarios (solo Administrador) ──────────────────────────
    path('register/',        RegisterView.as_view(),       name='auth-register'),
    path('users/',           UserListView.as_view(),        name='auth-users-list'),
    path('users/<int:pk>/',  UserDetailView.as_view(),     name='auth-users-detail'),
]