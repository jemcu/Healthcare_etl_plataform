from rest_framework import serializers
from .models import MLModel, Prediction, AlgoritmoChoices


class MLModelSerializer(serializers.ModelSerializer):
    entrenado_por_nombre = serializers.SerializerMethodField()
    algoritmo_display    = serializers.CharField(source='get_algoritmo_display', read_only=True)

    class Meta:
        model  = MLModel
        fields = [
            'id', 'nombre', 'algoritmo', 'algoritmo_display', 'version',
            'estado', 'activo',
            'accuracy', 'precision', 'recall', 'f1_score', 'roc_auc',
            'matriz_confusion', 'registros_entrenamiento',
            'features_usadas', 'entrenado_por_nombre', 'creado_en',
        ]

    def get_entrenado_por_nombre(self, obj):
        if obj.entrenado_por:
            return obj.entrenado_por.get_full_name() or obj.entrenado_por.username
        return 'Sistema'


class TrainRequestSerializer(serializers.Serializer):
    algoritmo = serializers.ChoiceField(
        choices=AlgoritmoChoices.choices,
        default=AlgoritmoChoices.RANDOM_FOREST,
    )
    nombre = serializers.CharField(max_length=100, required=False, default='')


class PredictionSerializer(serializers.ModelSerializer):
    modelo_nombre = serializers.CharField(source='modelo.nombre', read_only=True)

    class Meta:
        model  = Prediction
        fields = [
            'id', 'modelo_nombre', 'paciente',
            'datos_entrada', 'riesgo_predicho',
            'probabilidad', 'probabilidades_dict',
            'creado_en',
        ]


class PredictRequestSerializer(serializers.Serializer):
    """Datos de entrada para predecir el riesgo de UN paciente."""
    edad                    = serializers.FloatField()
    peso                    = serializers.FloatField()
    altura                  = serializers.FloatField()
    imc                     = serializers.FloatField(required=False, default=0)
    presion_sistolica       = serializers.FloatField()
    presion_diastolica      = serializers.FloatField()
    frecuencia_cardiaca     = serializers.FloatField()
    glucosa                 = serializers.FloatField()
    colesterol              = serializers.FloatField()
    saturacion_oxigeno      = serializers.FloatField()
    temperatura             = serializers.FloatField()
    fumador                 = serializers.BooleanField(default=False)
    consumo_alcohol         = serializers.BooleanField(default=False)
    antecedentes_familiares = serializers.BooleanField(default=False)
    paciente_id             = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        # Calcular IMC si no viene
        if not data.get('imc') and data.get('peso') and data.get('altura'):
            try:
                data['imc'] = round(data['peso'] / (data['altura'] ** 2), 2)
            except ZeroDivisionError:
                data['imc'] = 0.0
        return data