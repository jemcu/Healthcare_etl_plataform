from django.shortcuts import render

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Paciente
from .serializers import (
    PacienteListSerializer,
    PacienteDetailSerializer,
    PacienteCreateSerializer,
)
from .services.extractor import get_pacientes_queryset
from .services.loader import crear_paciente, actualizar_paciente, recalcular_todos_los_riesgos

logger = logging.getLogger(__name__)

PAGE_SIZE = 20


class PacienteListView(APIView):
    """
    GET  /api/pacientes/          → Lista paginada con filtros
    POST /api/pacientes/          → Crear paciente nuevo
    
    Filtros GET disponibles:
      ?riesgo=Alto
      ?sexo=Femenino
      ?edad_min=18&edad_max=60
      ?diagnostico=diabetes
      ?criticos=true
      ?page=1
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Filtros desde query params
        riesgo      = request.query_params.get('riesgo')
        sexo        = request.query_params.get('sexo')
        edad_min    = request.query_params.get('edad_min')
        edad_max    = request.query_params.get('edad_max')
        diagnostico = request.query_params.get('diagnostico')
        criticos    = request.query_params.get('criticos', '').lower() == 'true'
        page        = int(request.query_params.get('page', 1))

        qs = get_pacientes_queryset(
            riesgo=riesgo,
            sexo=sexo,
            edad_min=int(edad_min) if edad_min else None,
            edad_max=int(edad_max) if edad_max else None,
            diagnostico=diagnostico,
            criticos_only=criticos,
        )

        total = qs.count()

        # Paginación simple
        offset = (page - 1) * PAGE_SIZE
        pacientes = qs[offset: offset + PAGE_SIZE]

        serializer = PacienteListSerializer(pacientes, many=True)
        return Response({
            'total':       total,
            'pagina':      page,
            'paginas':     (total + PAGE_SIZE - 1) // PAGE_SIZE,
            'resultados':  serializer.data,
        })

    def post(self, request):
        serializer = PacienteCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            paciente = crear_paciente(serializer.validated_data)
            return Response(
                PacienteDetailSerializer(paciente).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            logger.error(f"[PATIENTS] Error creando paciente: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PacienteDetailView(APIView):
    """
    GET    /api/pacientes/<id>/   → Detalle completo
    PUT    /api/pacientes/<id>/   → Actualizar completamente
    PATCH  /api/pacientes/<id>/   → Actualizar parcialmente
    DELETE /api/pacientes/<id>/   → Eliminar
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Paciente.objects.get(pk=pk)
        except Paciente.DoesNotExist:
            return None

    def get(self, request, pk):
        paciente = self.get_object(pk)
        if not paciente:
            return Response({'error': 'Paciente no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(PacienteDetailSerializer(paciente).data)

    def put(self, request, pk):
        paciente = self.get_object(pk)
        if not paciente:
            return Response({'error': 'Paciente no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PacienteCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        paciente = actualizar_paciente(paciente, serializer.validated_data)
        return Response(PacienteDetailSerializer(paciente).data)

    def patch(self, request, pk):
        paciente = self.get_object(pk)
        if not paciente:
            return Response({'error': 'Paciente no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PacienteCreateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        paciente = actualizar_paciente(paciente, serializer.validated_data)
        return Response(PacienteDetailSerializer(paciente).data)

    def delete(self, request, pk):
        paciente = self.get_object(pk)
        if not paciente:
            return Response({'error': 'Paciente no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        nombre = paciente.nombre_completo
        paciente.delete()
        return Response({'mensaje': f'Paciente "{nombre}" eliminado.'}, status=status.HTTP_200_OK)


class PacienteCriticosView(APIView):
    """
    GET /api/pacientes/criticos/
    Lista pacientes que superan umbrales críticos:
    presion_sistolica > 180 | glucosa > 300 | saturacion_oxigeno < 85
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = get_pacientes_queryset(criticos_only=True)
        serializer = PacienteListSerializer(qs, many=True)
        return Response({
            'total': qs.count(),
            'pacientes': serializer.data,
        })


class RecalcularRiesgosView(APIView):
    """
    POST /api/pacientes/recalcular/
    Recalcula el IMC y nivel de riesgo de todos los pacientes en BD.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            count = recalcular_todos_los_riesgos()
            return Response({'mensaje': f'Riesgo recalculado para {count} pacientes.'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PacienteStatsView(APIView):
    """
    GET /api/pacientes/stats/
    Resumen rápido: total, por riesgo, por sexo.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from django.db.models import Count, Avg

        total = Paciente.objects.count()
        if total == 0:
            return Response({'total': 0})

        por_riesgo = dict(
            Paciente.objects.values_list('riesgo_enfermedad')
            .annotate(n=Count('id_paciente'))
            .values_list('riesgo_enfermedad', 'n')
        )

        por_sexo = dict(
            Paciente.objects.values_list('sexo')
            .annotate(n=Count('id_paciente'))
            .values_list('sexo', 'n')
        )

        promedios = Paciente.objects.aggregate(
            avg_edad=Avg('edad'),
            avg_imc=Avg('imc'),
            avg_glucosa=Avg('glucosa'),
            avg_presion=Avg('presion_sistolica'),
        )

        return Response({
            'total': total,
            'por_riesgo': por_riesgo,
            'por_sexo': por_sexo,
            'promedios': {k: round(v, 2) if v else 0 for k, v in promedios.items()},
        })