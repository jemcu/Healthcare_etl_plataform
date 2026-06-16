from rest_framework import serializers
from .models import ETLLog


class ETLLogSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()
    duracion = serializers.CharField(source='duracion_formateada', read_only=True)

    class Meta:
        model = ETLLog
        fields = [
            'id', 'usuario_nombre', 'fecha_inicio', 'fecha_fin',
            'archivo_origen', 'tipo_origen',
            'registros_extraidos', 'registros_limpios', 'registros_cargados',
            'duplicados_removidos', 'nulos_tratados',
            'outliers_corregidos', 'errores_tipo_corregidos',
            'tiempo_ejecucion', 'duracion', 'estado', 'mensaje',
        ]

    def get_usuario_nombre(self, obj):
        if obj.usuario:
            return obj.usuario.get_full_name() or obj.usuario.username
        return 'Sistema'


class ETLRunSerializer(serializers.Serializer):
    """Serializa la respuesta de /api/etl/run/"""
    estado = serializers.CharField()
    archivo = serializers.CharField()
    tiempo_total = serializers.FloatField()
    mensaje = serializers.CharField()
    extract = serializers.DictField()
    transform = serializers.DictField()
    load = serializers.DictField()


class UploadFileSerializer(serializers.Serializer):
    archivo = serializers.FileField()
    tipo = serializers.ChoiceField(
        choices=[('excel', 'Excel'), ('csv', 'CSV')],
        default='excel'
    )