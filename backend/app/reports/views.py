from django.shortcuts import render
import logging
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import ReporteLog, FormatoChoices, ReporteTipo
from .services.pdf_generator import (
    generar_pdf_pacientes, generar_pdf_analitica, generar_pdf_ml,
)
from .services.excel_generator import (
    generar_excel_pacientes, generar_excel_analitica, generar_excel_ml,
)
from .services.csv_generator import generar_csv_pacientes, generar_csv_etl

logger = logging.getLogger(__name__)


def _log_reporte(usuario, tipo, formato, filas, filtros=None):
    ReporteLog.objects.create(
        tipo=tipo, formato=formato,
        filas=filas, filtros=filtros or {},
        generado_por=usuario,
    )


# ── Helpers de respuesta HTTP ─────────────────────────────────────────────────

def _pdf_response(content: bytes, filename: str) -> HttpResponse:
    resp = HttpResponse(content, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


def _excel_response(content: bytes, filename: str) -> HttpResponse:
    resp = HttpResponse(
        content,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


def _csv_response(content: bytes, filename: str) -> HttpResponse:
    resp = HttpResponse(content, content_type='text/csv; charset=utf-8-sig')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


# ── Vistas ────────────────────────────────────────────────────────────────────

class ReportePacientesView(APIView):
    """
    GET /api/reportes/pacientes/?formato=pdf|excel|csv
    Filtros opcionales: riesgo, sexo, edad_min, edad_max, diagnostico, criticos
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from patients.services.extractor import get_pacientes_queryset

        formato     = request.query_params.get('formato', 'pdf').lower()
        riesgo      = request.query_params.get('riesgo')
        sexo        = request.query_params.get('sexo')
        edad_min    = request.query_params.get('edad_min')
        edad_max    = request.query_params.get('edad_max')
        diagnostico = request.query_params.get('diagnostico')
        criticos    = request.query_params.get('criticos', '').lower() == 'true'

        filtros = {k: v for k, v in {
            'riesgo': riesgo, 'sexo': sexo,
            'edad_min': edad_min, 'edad_max': edad_max,
            'diagnostico': diagnostico,
        }.items() if v}

        qs = get_pacientes_queryset(
            riesgo=riesgo, sexo=sexo,
            edad_min=int(edad_min) if edad_min else None,
            edad_max=int(edad_max) if edad_max else None,
            diagnostico=diagnostico,
            criticos_only=criticos,
        )
        total = qs.count()

        try:
            if formato == 'pdf':
                content = generar_pdf_pacientes(qs, filtros)
                _log_reporte(request.user, ReporteTipo.PACIENTES, FormatoChoices.PDF, total, filtros)
                return _pdf_response(content, 'reporte_pacientes.pdf')

            elif formato == 'excel':
                content = generar_excel_pacientes(qs, filtros)
                _log_reporte(request.user, ReporteTipo.PACIENTES, FormatoChoices.EXCEL, total, filtros)
                return _excel_response(content, 'reporte_pacientes.xlsx')

            elif formato == 'csv':
                content = generar_csv_pacientes(qs)
                _log_reporte(request.user, ReporteTipo.PACIENTES, FormatoChoices.CSV, total, filtros)
                return _csv_response(content, 'reporte_pacientes.csv')

            return Response({'error': 'Formato inválido. Usa: pdf, excel, csv'},
                            status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"[REPORTS] Error generando reporte pacientes: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReporteAnaliticaView(APIView):
    """
    GET /api/reportes/analitica/?formato=pdf|excel
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from analytics.services.kpi_calculator import calcular_kpis

        formato = request.query_params.get('formato', 'pdf').lower()

        try:
            kpis = calcular_kpis()
            total = kpis.get('total_pacientes', 0)

            if formato == 'pdf':
                content = generar_pdf_analitica(kpis)
                _log_reporte(request.user, ReporteTipo.ANALITICA, FormatoChoices.PDF, total)
                return _pdf_response(content, 'reporte_analitica.pdf')

            elif formato == 'excel':
                content = generar_excel_analitica(kpis)
                _log_reporte(request.user, ReporteTipo.ANALITICA, FormatoChoices.EXCEL, total)
                return _excel_response(content, 'reporte_analitica.xlsx')

            return Response({'error': 'Formato inválido. Usa: pdf, excel'},
                            status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"[REPORTS] Error reporte analítica: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReporteMLView(APIView):
    """
    GET /api/reportes/ml/?formato=pdf|excel
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from ml.models import MLModel, EstadoChoices
        from ml.serializers import MLModelSerializer

        formato = request.query_params.get('formato', 'pdf').lower()
        modelo = MLModel.objects.filter(activo=True, estado=EstadoChoices.LISTO).first()

        if not modelo:
            return Response({'error': 'No hay modelo activo para reportar.'},
                            status=status.HTTP_404_NOT_FOUND)

        modelo_data = MLModelSerializer(modelo).data
        metricas = {
            'accuracy':  modelo.accuracy,
            'precision': modelo.precision,
            'recall':    modelo.recall,
            'f1_score':  modelo.f1_score,
            'roc_auc':   modelo.roc_auc,
        }

        try:
            if formato == 'pdf':
                content = generar_pdf_ml(modelo_data, metricas)
                _log_reporte(request.user, ReporteTipo.ML, FormatoChoices.PDF, 0)
                return _pdf_response(content, 'reporte_ml.pdf')

            elif formato == 'excel':
                content = generar_excel_ml(modelo_data, metricas)
                _log_reporte(request.user, ReporteTipo.ML, FormatoChoices.EXCEL, 0)
                return _excel_response(content, 'reporte_ml.xlsx')

            return Response({'error': 'Formato inválido. Usa: pdf, excel'},
                            status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"[REPORTS] Error reporte ML: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReporteETLView(APIView):
    """
    GET /api/reportes/etl/?formato=pdf|csv
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from etl.models import ETLLog
        from etl.serializers import ETLLogSerializer

        formato = request.query_params.get('formato', 'csv').lower()
        logs = ETLLog.objects.all()[:100]

        try:
            if formato == 'csv':
                content = generar_csv_etl(logs)
                _log_reporte(request.user, ReporteTipo.ETL, FormatoChoices.CSV, logs.count())
                return _csv_response(content, 'reporte_etl.csv')

            elif formato == 'pdf':
                # Devuelve JSON si no hay generador PDF específico para ETL
                data = ETLLogSerializer(logs, many=True).data
                _log_reporte(request.user, ReporteTipo.ETL, FormatoChoices.PDF, logs.count())
                return Response({'reportes_etl': data})

            return Response({'error': 'Formato inválido. Usa: pdf, csv'},
                            status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"[REPORTS] Error reporte ETL: {e}", exc_info=True)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ReporteHistorialView(APIView):
    """
    GET /api/reportes/historial/
    Lista los últimos 50 reportes generados.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .serializers import ReporteLogSerializer
        logs = ReporteLog.objects.all()[:50]
        from .serializers import ReporteLogSerializer
        return Response({
            'total': ReporteLog.objects.count(),
            'reportes': ReporteLogSerializer(logs, many=True).data,
        })