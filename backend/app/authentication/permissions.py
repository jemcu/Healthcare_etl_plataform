from rest_framework.permissions import BasePermission
from .models import Role


class IsAdministrador(BasePermission):
    """Solo usuarios con rol Administrador."""
    message = 'Acceso restringido a Administradores.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.rol == Role.ADMINISTRADOR
        )


class IsMedico(BasePermission):
    """Solo usuarios con rol Médico."""
    message = 'Acceso restringido a Médicos.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.rol == Role.MEDICO
        )


class IsAnalista(BasePermission):
    """Solo usuarios con rol Analista."""
    message = 'Acceso restringido a Analistas.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.rol == Role.ANALISTA
        )


class IsAdministradorOrMedico(BasePermission):
    """Administrador o Médico."""
    message = 'Acceso restringido a Administradores y Médicos.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.rol in [Role.ADMINISTRADOR, Role.MEDICO]
        )


class IsAdministradorOrAnalista(BasePermission):
    """Administrador o Analista."""
    message = 'Acceso restringido a Administradores y Analistas.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.rol in [Role.ADMINISTRADOR, Role.ANALISTA]
        )