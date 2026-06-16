from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'email', 'get_full_name', 'rol', 'activo', 'creado_en']
    list_filter   = ['rol', 'activo', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering      = ['-creado_en']

    fieldsets = UserAdmin.fieldsets + (
        ('Datos del rol', {'fields': ('rol', 'telefono', 'activo')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Datos del rol', {'fields': ('rol', 'telefono', 'email', 'first_name', 'last_name')}),
    )