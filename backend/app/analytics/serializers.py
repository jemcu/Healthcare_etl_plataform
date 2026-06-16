from rest_framework import serializers
from .models import ClinicalSnapshot


class ClinicalSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalSnapshot
        fields = '__all__'


class KPIResponseSerializer(serializers.Serializer):
    total_pacientes = serializers.IntegerField()
    pacientes_criticos = serializers.IntegerField()
    pacientes_hipertensos = serializers.IntegerField()
    porcentaje_hipertensos = serializers.FloatField()
    pacientes_diabeticos = serializers.IntegerField()
    porcentaje_diabeticos = serializers.FloatField()
    pacientes_fumadores = serializers.IntegerField()
    porcentaje_fumadores = serializers.FloatField()
    distribucion_riesgo = serializers.DictField()
    distribucion_imc = serializers.DictField()
    promedios = serializers.DictField()


class DescriptiveStatsSerializer(serializers.Serializer):
    """
    Serializa el dict { variable: { media, mediana, moda, ... } }
    """
    def to_representation(self, instance):
        return instance