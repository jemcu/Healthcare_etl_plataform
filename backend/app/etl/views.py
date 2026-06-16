from django.shortcuts import render

import os
import tempfile
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .models import ETLLog, ETLStatus
from .serializers import ETLLogSerializer, ETLRunSerializer, UploadFileSerializer
from .services.pipeline import run_etl_pipeline, DEFAULT_DATASET_PATH

logger = logging.getLogger(__name__)


class RunETLView(APIView):
    """
    POST /api/etl/run/
    Ejecuta el pipeline ETL completo sobre el dataset por defecto.
    Solo Administradores y Analistas.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Crear log de inicio
        etl_log = ETLLog.objects.create(
            usuario=request.user,
            estado=ETLStatus.EJECUTANDO,
            archivo_origen=os.path.basename(DEFAULT_DATASET_PATH),
        )

        resultado = run_etl_pipeline(
            filepath=DEFAULT_DATASET_PATH,
            etl_log=etl_log,
            tipo='excel',
        )

        http_status = (
            status.HTTP_200_OK
            if resultado['estado'] == 'EXITOSO'
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return Response(resultado, status=http_status)


class UploadAndRunETLView(APIView):
    """
    POST /api/etl/upload/
    Permite subir un archivo Excel o CSV y ejecutar ETL sobre él.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = UploadFileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        archivo = serializer.validated_data['archivo']
        tipo = serializer.validated_data['tipo']

        # Guardar temporalmente el archivo subido
        suffix = '.xlsx' if tipo == 'excel' else '.csv'
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            for chunk in archivo.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        etl_log = ETLLog.objects.create(
            usuario=request.user,
            estado=ETLStatus.EJECUTANDO,
            archivo_origen=archivo.name,
            tipo_origen=tipo,
        )

        try:
            resultado = run_etl_pipeline(
                filepath=tmp_path,
                etl_log=etl_log,
                tipo=tipo,
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        http_status = (
            status.HTTP_200_OK
            if resultado['estado'] == 'EXITOSO'
            else status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        return Response(resultado, status=http_status)


class ETLHistoryView(APIView):
    """
    GET /api/etl/history/
    Lista los últimos 50 registros de ejecuciones ETL.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = ETLLog.objects.all()[:50]
        serializer = ETLLogSerializer(logs, many=True)
        return Response({
            'total': ETLLog.objects.count(),
            'resultados': serializer.data,
        })


class ETLLogDetailView(APIView):
    """
    GET /api/etl/history/<id>/
    Detalle completo de un log ETL específico (incluye errores).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            log = ETLLog.objects.get(pk=pk)
        except ETLLog.DoesNotExist:
            return Response({'error': 'Log no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        data = ETLLogSerializer(log).data
        data['detalle_errores'] = log.detalle_errores
        return Response(data)


class ETLStatusView(APIView):
    """
    GET /api/etl/status/
    Retorna el estado del último proceso ETL ejecutado.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        ultimo = ETLLog.objects.first()
        if not ultimo:
            return Response({'mensaje': 'No hay ejecuciones ETL registradas.'})
        return Response(ETLLogSerializer(ultimo).data)