from rest_framework import serializers
from .models import ReporteLog


class ReporteLogSerializer(serializers.ModelSerializer):
    generado_por_nombre = serializers.SerializerMethodField()
    tipo_display        = serializers.CharField(source='get_tipo_display',   read_only=True)
    formato_display     = serializers.CharField(source='get_formato_display', read_only=True)

    class Meta:
        model  = ReporteLog
        fields = [
            'id', 'tipo', 'tipo_display', 'formato', 'formato_display',
            'filas', 'filtros', 'generado_por_nombre', 'creado_en',
        ]

    def get_generado_por_nombre(self, obj):
        if obj.generado_por:
            return obj.generado_por.get_full_name() or obj.generado_por.username
        return 'Sistema'