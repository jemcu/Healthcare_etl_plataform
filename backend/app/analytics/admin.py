from django.contrib import admin
from django.contrib import admin
from .models import ClinicalSnapshot


@admin.register(ClinicalSnapshot)
class ClinicalSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        'fecha_calculo', 'total_pacientes', 'pacientes_criticos',
        'pacientes_hipertensos', 'pacientes_diabeticos', 'promedio_imc'
    ]
    list_filter = ['fecha_calculo']
    readonly_fields = ['fecha_calculo']
    ordering = ['-fecha_calculo']
