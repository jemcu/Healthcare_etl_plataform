from django.shortcuts import render
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import MLModel, Prediction, EstadoChoices
from .serializers import (
    MLModelSerializer,
    TrainRequestSerializer,
    PredictionSerializer,
    PredictRequestSerializer,
)
from .services.trainer import train_model
from .services.evaluator import evaluar_modelo
from .services.predictor import predecir_riesgo

logger = logging.getLogger(__name__)


class TrainModelView(APIView):
    """
    POST /api/ml/train/
    Entrena un nuevo modelo ML con los datos actuales de la BD.
    Body: { algoritmo: 'random_forest' | 'logistic_regression' | 'decision_tree', nombre: '' }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = TrainRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        algoritmo = serializer.validated_data['algoritmo']
        nombre    = serializer.validated_data['nombre'] or f"Modelo {algoritmo.replace('_', ' ').title()}"

        # Calcular versión
        version = MLModel.objects.filter(algoritmo=algoritmo).count() + 1

        # Crear registro en BD con estado ENTRENANDO
        ml_model = MLModel.objects.create(
            nombre=nombre,
            algoritmo=algoritmo,
            version=version,
            estado=EstadoChoices.ENTRENANDO,
            entrenado_por=request.user,
        )

        try:
            # Entrenar
            train_result = train_model(algoritmo=algoritmo, ml_model_instance=ml_model)

            # Evaluar
            metricas = evaluar_modelo(
                pipeline=train_result['pipeline'],
                X_test=train_result['X_test'],
                y_test=train_result['y_test'],
            )

            # Desactivar modelos anteriores del mismo algoritmo
            MLModel.objects.filter(algoritmo=algoritmo, activo=True).update(activo=False)

            # Actualizar registro con métricas
            ml_model.estado                  = EstadoChoices.LISTO
            ml_model.activo                  = True
            ml_model.accuracy                = metricas['accuracy']
            ml_model.precision               = metricas['precision']
            ml_model.recall                  = metricas['recall']
            ml_model.f1_score                = metricas['f1_score']
            ml_model.roc_auc                 = metricas.get('roc_auc')
            ml_model.matriz_confusion        = metricas['matriz_confusion']
            ml_model.registros_entrenamiento = train_result['registros_entrenamiento']
            ml_model.features_usadas         = train_result['feature_names']
            ml_model.ruta_archivo            = train_result['ruta_archivo']
            ml_model.save()

            return Response({
                'modelo': MLModelSerializer(ml_model).data,
                'metricas': metricas,
                'entrenamiento': {
                    'registros_train': train_result['registros_entrenamiento'],
                    'registros_test':  train_result['registros_prueba'],
                    'tiempo_segundos': train_result['tiempo_entrenamiento'],
                    'distribucion_clases': train_result['distribucion_clases'],
                },
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            ml_model.estado = EstadoChoices.ERROR
            ml_model.mensaje_error = str(e)
            ml_model.save()
            logger.error(f"[ML] Error entrenando: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ModelListView(APIView):
    """
    GET /api/ml/models/
    Lista todos los modelos entrenados ordenados por fecha.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        models = MLModel.objects.all()
        return Response({
            'total': models.count(),
            'modelos': MLModelSerializer(models, many=True).data,
        })


class ModelDetailView(APIView):
    """
    GET   /api/ml/models/<id>/   → Detalle + métricas completas
    PATCH /api/ml/models/<id>/   → Activar como modelo en producción
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return MLModel.objects.get(pk=pk)
        except MLModel.DoesNotExist:
            return None

    def get(self, request, pk):
        obj = self.get_object(pk)
        if not obj:
            return Response({'error': 'Modelo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(MLModelSerializer(obj).data)

    def patch(self, request, pk):
        """Activar este modelo como el modelo en producción."""
        obj = self.get_object(pk)
        if not obj:
            return Response({'error': 'Modelo no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if obj.estado != EstadoChoices.LISTO:
            return Response({'error': 'Solo se puede activar un modelo en estado LISTO.'}, status=status.HTTP_400_BAD_REQUEST)

        MLModel.objects.filter(activo=True).update(activo=False)
        obj.activo = True
        obj.save()
        return Response({'mensaje': f'Modelo "{obj.nombre}" activado en producción.'})


class PredictView(APIView):
    """
    POST /api/ml/predict/
    Predice el nivel de riesgo de un paciente con los datos clínicos enviados.
    Usa el modelo activo en producción.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PredictRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        datos = serializer.validated_data
        paciente_id = datos.pop('paciente_id', None)

        try:
            resultado = predecir_riesgo(datos)

            # Guardar predicción en BD
            modelo_activo = MLModel.objects.filter(activo=True, estado=EstadoChoices.LISTO).first()
            prediccion = Prediction.objects.create(
                modelo=modelo_activo,
                paciente_id=paciente_id,
                datos_entrada=datos,
                riesgo_predicho=resultado['riesgo_predicho'],
                probabilidad=resultado.get('probabilidad'),
                probabilidades_dict=resultado.get('probabilidades', {}),
                realizado_por=request.user,
            )

            return Response({
                'prediccion_id':  prediccion.pk,
                'riesgo_predicho': resultado['riesgo_predicho'],
                'probabilidad':    resultado.get('probabilidad'),
                'probabilidades':  resultado.get('probabilidades', {}),
                'modelo_usado':    resultado.get('modelo_usado', ''),
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"[PREDICT] Error: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MetricsView(APIView):
    """
    GET /api/ml/metrics/
    Retorna las métricas del modelo activo en producción.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        modelo = MLModel.objects.filter(activo=True, estado=EstadoChoices.LISTO).first()
        if not modelo:
            return Response({'error': 'No hay ningún modelo activo.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'modelo': MLModelSerializer(modelo).data,
            'metricas': {
                'accuracy':          modelo.accuracy,
                'precision':         modelo.precision,
                'recall':            modelo.recall,
                'f1_score':          modelo.f1_score,
                'roc_auc':           modelo.roc_auc,
                'matriz_confusion':  modelo.matriz_confusion,
            },
        })


class PredictionHistoryView(APIView):
    """
    GET /api/ml/predictions/
    Lista las últimas 100 predicciones realizadas.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        preds = Prediction.objects.select_related('modelo', 'paciente').all()[:100]
        return Response({
            'total': Prediction.objects.count(),
            'predicciones': PredictionSerializer(preds, many=True).data,
        })