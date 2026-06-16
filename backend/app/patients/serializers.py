from rest_framework import serializers
from .models import Paciente


class PacienteListSerializer(serializers.ModelSerializer):
    """Versión resumida para listados (menos campos)."""
    nombre_completo = serializers.CharField(read_only=True)
    es_critico      = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Paciente
        fields = [
            'id_paciente', 'nombre_completo', 'edad', 'sexo',
            'imc', 'clasificacion_imc',
            'presion_sistolica', 'glucosa', 'saturacion_oxigeno',
            'riesgo_enfermedad', 'diagnostico_preliminar',
            'fecha_consulta', 'es_critico',
        ]


class PacienteDetailSerializer(serializers.ModelSerializer):
    """Versión completa con todos los campos."""
    nombre_completo = serializers.CharField(read_only=True)
    es_critico      = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Paciente
        fields = '__all__'
        read_only_fields = ['id_paciente', 'imc', 'clasificacion_imc',
                            'riesgo_enfermedad', 'creado_en', 'actualizado_en']


class PacienteCreateSerializer(serializers.ModelSerializer):
    """Para crear o actualizar un paciente via API."""

    class Meta:
        model  = Paciente
        fields = [
            'nombres', 'apellidos', 'edad', 'sexo',
            'peso', 'altura',
            'presion_sistolica', 'presion_diastolica', 'frecuencia_cardiaca',
            'glucosa', 'colesterol', 'saturacion_oxigeno', 'temperatura',
            'antecedentes_familiares', 'fumador', 'consumo_alcohol',
            'actividad_fisica', 'diagnostico_preliminar', 'fecha_consulta',
        ]

    def validate_edad(self, value):
        if not (0 <= value <= 120):
            raise serializers.ValidationError('La edad debe estar entre 0 y 120 años.')
        return value

    def validate_peso(self, value):
        if not (2 <= value <= 300):
            raise serializers.ValidationError('El peso debe estar entre 2 y 300 kg.')
        return value

    def validate_altura(self, value):
        if not (0.5 <= value <= 2.5):
            raise serializers.ValidationError('La altura debe estar entre 0.5 y 2.5 metros.')
        return value

    def validate_glucosa(self, value):
        if not (30 <= value <= 600):
            raise serializers.ValidationError('La glucosa debe estar entre 30 y 600 mg/dL.')
        return value

    def validate_saturacion_oxigeno(self, value):
        if not (60 <= value <= 100):
            raise serializers.ValidationError('La saturación de oxígeno debe estar entre 60 y 100%.')
        return value