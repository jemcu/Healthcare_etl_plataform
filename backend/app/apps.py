from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'analytics'
    verbose_name = 'Analítica Clínica'

from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'
    verbose_name = 'Autenticación y Roles'

    from django.apps import AppConfig


class EtlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'etl'
    verbose_name = 'Proceso ETL'

class PatientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patients'
    verbose_name = 'Pacientes Clínicos'
 