from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMINISTRADOR = 'administrador', 'Administrador'
    MEDICO        = 'medico',        'Médico'
    ANALISTA      = 'analista',      'Analista'


class CustomUser(AbstractUser):
    """
    Usuario personalizado con campo de rol para control de acceso.
    Extiende AbstractUser → hereda username, email, password, first_name, last_name.
    """
    rol = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.ANALISTA,
    )
    telefono = models.CharField(max_length=20, blank=True, null=True)
    activo   = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'auth_custom_user'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-creado_en']

    def __str__(self):
        return f"{self.get_full_name()} ({self.rol})"

    @property
    def is_administrador(self):
        return self.rol == Role.ADMINISTRADOR

    @property
    def is_medico(self):
        return self.rol == Role.MEDICO

    @property
    def is_analista(self):
        return self.rol == Role.ANALISTA