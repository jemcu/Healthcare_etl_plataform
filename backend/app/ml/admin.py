from django.contrib import admin

from django.contrib import admin
from .models import MLModel, Prediction


@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display  = ['nombre', 'algoritmo', 'version', 'estado', 'activo',
                     'accuracy', 'f1_score', 'registros_entrenamiento', 'creado_en']
    list_filter   = ['algoritmo', 'estado', 'activo']
    search_fields = ['nombre']
    readonly_fields = ['creado_en', 'actualizado_en', 'ruta_archivo',
                       'matriz_confusion', 'features_usadas']
    ordering = ['-creado_en']

    actions = ['activar_modelo']

    def activar_modelo(self, request, queryset):
        MLModel.objects.filter(activo=True).update(activo=False)
        obj = queryset.first()
        obj.activo = True
        obj.save()
        self.message_user(request, f'Modelo "{obj.nombre}" activado.')
    activar_modelo.short_description = 'Activar modelo seleccionado en producción'


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display  = ['id', 'riesgo_predicho', 'probabilidad', 'modelo', 'paciente', 'realizado_por', 'creado_en']
    list_filter   = ['riesgo_predicho', 'creado_en']
    readonly_fields = ['creado_en', 'datos_entrada', 'probabilidades_dict']
    ordering = ['-creado_en']