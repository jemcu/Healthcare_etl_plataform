from django.apps import AppConfig


class EtlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app.etl'
    verbose_name = 'Proceso ETL'

