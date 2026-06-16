from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .services.kpi_calculator import calcular_kpis
from .services.descriptive_stats import calcular_estadisticas_descriptivas
from .services.segmentation import (
    segmentar_por_edad,
    segmentar_por_sexo,
    segmentar_por_riesgo,
    segmentar_por_diagnostico,
    segmentar_por_imc,
    obtener_pacientes_criticos,
)
from .models import ClinicalSnapshot
from .serializers import ClinicalSnapshotSerializer


class KPIView(APIView):
    """
    GET /api/analytics/kpis/
    Retorna los KPIs médicos principales del dashboard.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = calcular_kpis()
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Error calculando KPIs: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DescriptiveStatsView(APIView):
    """
    GET /api/analytics/stats/
    Retorna estadísticas descriptivas (media, mediana, moda, desv. std)
    de todas las variables numéricas clínicas.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = calcular_estadisticas_descriptivas()
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Error calculando estadísticas: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SegmentationView(APIView):
    """
    GET /api/analytics/segments/?by=edad|sexo|riesgo|diagnostico|imc
    Retorna segmentación de pacientes según el parámetro solicitado.
    """
    permission_classes = [IsAuthenticated]

    SEGMENT_MAP = {
        'edad': segmentar_por_edad,
        'sexo': segmentar_por_sexo,
        'riesgo': segmentar_por_riesgo,
        'diagnostico': segmentar_por_diagnostico,
        'imc': segmentar_por_imc,
    }

    def get(self, request):
        by = request.query_params.get('by', 'riesgo')

        if by not in self.SEGMENT_MAP:
            return Response(
                {'error': f'Parámetro "by" inválido. Opciones: {list(self.SEGMENT_MAP.keys())}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = self.SEGMENT_MAP[by]()
            return Response({'segmento': by, 'data': data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Error en segmentación: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CriticalPatientsView(APIView):
    """
    GET /api/analytics/criticos/
    Lista pacientes que superan umbrales clínicos críticos:
    - Presión sistólica > 180
    - Glucosa > 300
    - Saturación O2 < 85
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            data = obtener_pacientes_criticos()
            return Response(
                {'total': len(data), 'pacientes': data},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': f'Error obteniendo pacientes críticos: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DashboardSummaryView(APIView):
    """
    GET /api/analytics/dashboard/
    Endpoint unificado: devuelve KPIs + segmentaciones en una sola llamada
    para cargar el dashboard completo con un solo request.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            return Response({
                'kpis': calcular_kpis(),
                'segmentacion_riesgo': segmentar_por_riesgo(),
                'segmentacion_edad': segmentar_por_edad(),
                'segmentacion_sexo': segmentar_por_sexo(),
                'segmentacion_imc': segmentar_por_imc(),
                'top_diagnosticos': segmentar_por_diagnostico(),
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': f'Error cargando dashboard: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SnapshotView(APIView):
    """
    POST /api/analytics/snapshot/   → Guarda snapshot actual de KPIs
    GET  /api/analytics/snapshot/   → Lista snapshots históricos
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        snapshots = ClinicalSnapshot.objects.all()[:20]
        serializer = ClinicalSnapshotSerializer(snapshots, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            kpis = calcular_kpis()
            dist = kpis.get('distribucion_riesgo', {})
            prom = kpis.get('promedios', {})

            snap = ClinicalSnapshot.objects.create(
                total_pacientes=kpis.get('total_pacientes', 0),
                pacientes_criticos=kpis.get('pacientes_criticos', 0),
                pacientes_alto_riesgo=dist.get('alto', 0),
                pacientes_medio_riesgo=dist.get('medio', 0),
                pacientes_bajo_riesgo=dist.get('bajo', 0),
                pacientes_hipertensos=kpis.get('pacientes_hipertensos', 0),
                pacientes_diabeticos=kpis.get('pacientes_diabeticos', 0),
                pacientes_fumadores=kpis.get('pacientes_fumadores', 0),
                promedio_edad=prom.get('edad', 0),
                promedio_imc=prom.get('imc', 0),
                promedio_glucosa=prom.get('glucosa', 0),
                promedio_colesterol=prom.get('colesterol', 0),
                promedio_presion_sistolica=prom.get('presion_sistolica', 0),
            )
            return Response(
                ClinicalSnapshotSerializer(snap).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': f'Error guardando snapshot: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
