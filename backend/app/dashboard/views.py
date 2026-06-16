import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


class DashboardSummaryView(APIView):
    """
    GET /api/dashboard/
    Endpoint principal del dashboard.
    Devuelve en UNA sola llamada:
      - KPIs clínicos
      - Segmentaciones (riesgo, edad, sexo, IMC)
      - Top diagnósticos
      - Último proceso ETL
      - Métricas del modelo ML activo
      - Últimas predicciones
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        resultado = {}
        errores   = []

        # ── KPIs y segmentaciones ─────────────────────────────────────────
        try:
            from analytics.services.kpi_calculator import calcular_kpis
            from analytics.services.segmentation import (
                segmentar_por_riesgo,
                segmentar_por_edad,
                segmentar_por_sexo,
                segmentar_por_imc,
                segmentar_por_diagnostico,
                obtener_pacientes_criticos,
            )
            resultado['kpis']               = calcular_kpis()
            resultado['segmentacion_riesgo'] = segmentar_por_riesgo()
            resultado['segmentacion_edad']   = segmentar_por_edad()
            resultado['segmentacion_sexo']   = segmentar_por_sexo()
            resultado['segmentacion_imc']    = segmentar_por_imc()
            resultado['top_diagnosticos']    = segmentar_por_diagnostico()
            resultado['pacientes_criticos']  = obtener_pacientes_criticos()[:10]
        except Exception as e:
            errores.append(f'analytics: {str(e)}')
            logger.warning(f'[DASHBOARD] Error en analytics: {e}')

        # ── Último ETL ────────────────────────────────────────────────────
        try:
            from etl.models import ETLLog
            from etl.serializers import ETLLogSerializer
            ultimo_etl = ETLLog.objects.first()
            resultado['ultimo_etl'] = (
                ETLLogSerializer(ultimo_etl).data if ultimo_etl else None
            )
            resultado['total_ejecuciones_etl'] = ETLLog.objects.count()
        except Exception as e:
            errores.append(f'etl: {str(e)}')
            logger.warning(f'[DASHBOARD] Error en etl: {e}')

        # ── Modelo ML activo ──────────────────────────────────────────────
        try:
            from ml.models import MLModel, EstadoChoices
            from ml.serializers import MLModelSerializer
            modelo = MLModel.objects.filter(
                activo=True, estado=EstadoChoices.LISTO
            ).first()
            resultado['modelo_ml'] = (
                MLModelSerializer(modelo).data if modelo else None
            )
        except Exception as e:
            errores.append(f'ml: {str(e)}')
            logger.warning(f'[DASHBOARD] Error en ml: {e}')

        # ── Últimas predicciones ──────────────────────────────────────────
        try:
            from ml.models import Prediction
            from ml.serializers import PredictionSerializer
            preds = Prediction.objects.select_related('modelo').all()[:5]
            resultado['ultimas_predicciones'] = PredictionSerializer(preds, many=True).data
        except Exception as e:
            errores.append(f'predicciones: {str(e)}')
            logger.warning(f'[DASHBOARD] Error en predicciones: {e}')

        # ── Estadísticas de reportes ──────────────────────────────────────
        try:
            from reports.models import ReporteLog
            resultado['total_reportes'] = ReporteLog.objects.count()
        except Exception as e:
            errores.append(f'reportes: {str(e)}')

        if errores:
            resultado['advertencias'] = errores

        return Response(resultado, status=status.HTTP_200_OK)


class DashboardKPIsView(APIView):
    """
    GET /api/dashboard/kpis/
    Solo los KPIs clínicos principales (respuesta más rápida).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            from analytics.services.kpi_calculator import calcular_kpis
            return Response(calcular_kpis())
        except Exception as e:
            logger.error(f'[DASHBOARD] Error KPIs: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardChartsView(APIView):
    """
    GET /api/dashboard/charts/
    Datos listos para alimentar los gráficos de Chart.js:
      - Barras: distribución por riesgo
      - Torta: distribución IMC
      - Línea: consultas por mes
      - Barras: top diagnósticos
      - Barras: distribución por sexo
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            from analytics.services.segmentation import (
                segmentar_por_riesgo,
                segmentar_por_imc,
                segmentar_por_diagnostico,
                segmentar_por_sexo,
            )
            from patients.models import Paciente
            from django.db.models import Count
            from django.db.models.functions import TruncMonth

            # Distribución por riesgo (barras)
            riesgo_raw = segmentar_por_riesgo()
            chart_riesgo = {
                'labels': [r['riesgo_enfermedad'] for r in riesgo_raw],
                'data':   [r['cantidad']          for r in riesgo_raw],
                'colors': ['#16a34a', '#eab308', '#f97316', '#dc2626'],
            }

            # Distribución IMC (torta)
            imc_raw = segmentar_por_imc()
            chart_imc = {
                'labels': list(imc_raw.keys()),
                'data':   list(imc_raw.values()),
            }

            # Top diagnósticos (barras horizontales)
            diag_raw = segmentar_por_diagnostico()
            chart_diagnosticos = {
                'labels': [d['diagnostico_preliminar'] for d in diag_raw],
                'data':   [d['cantidad']               for d in diag_raw],
            }

            # Por sexo (barras)
            sexo_raw = segmentar_por_sexo()
            chart_sexo = {
                'labels': [s['sexo']    for s in sexo_raw],
                'data':   [s['cantidad'] for s in sexo_raw],
            }

            # Consultas por mes (línea) — últimos 12 meses
            consultas_mes = (
                Paciente.objects
                .annotate(mes=TruncMonth('fecha_consulta'))
                .values('mes')
                .annotate(cantidad=Count('id_paciente'))
                .order_by('mes')
            )
            chart_consultas_mes = {
                'labels': [
                    c['mes'].strftime('%b %Y') if c['mes'] else 'Sin fecha'
                    for c in consultas_mes
                ],
                'data': [c['cantidad'] for c in consultas_mes],
            }

            return Response({
                'riesgo':        chart_riesgo,
                'imc':           chart_imc,
                'diagnosticos':  chart_diagnosticos,
                'sexo':          chart_sexo,
                'consultas_mes': chart_consultas_mes,
            })

        except Exception as e:
            logger.error(f'[DASHBOARD] Error charts: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardETLStatusView(APIView):
    """
    GET /api/dashboard/etl-status/
    Estado rápido del último proceso ETL ejecutado.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            from etl.models import ETLLog
            from etl.serializers import ETLLogSerializer

            ultimo = ETLLog.objects.first()
            if not ultimo:
                return Response({
                    'hay_datos': False,
                    'mensaje': 'No se ha ejecutado ningún proceso ETL aún.',
                })

            return Response({
                'hay_datos':          True,
                'ultimo_etl':         ETLLogSerializer(ultimo).data,
                'total_ejecuciones':  ETLLog.objects.count(),
                'exitosos':           ETLLog.objects.filter(estado='EXITOSO').count(),
                'con_error':          ETLLog.objects.filter(estado='ERROR').count(),
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DashboardMLStatusView(APIView):
    """
    GET /api/dashboard/ml-status/
    Estado del modelo ML activo y sus métricas.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            from ml.models import MLModel, Prediction, EstadoChoices
            from ml.serializers import MLModelSerializer

            modelo = MLModel.objects.filter(
                activo=True, estado=EstadoChoices.LISTO
            ).first()

            return Response({
                'modelo_activo':      MLModelSerializer(modelo).data if modelo else None,
                'total_modelos':      MLModel.objects.count(),
                'total_predicciones': Prediction.objects.count(),
                'predicciones_hoy':   Prediction.objects.filter(
                    creado_en__date=__import__('datetime').date.today()
                ).count(),
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)