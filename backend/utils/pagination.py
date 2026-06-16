"""
Clases de paginación personalizadas para HealthAnalytics IPS.
Extienden PageNumberPagination de DRF con respuestas estandarizadas.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """
    Paginación estándar: 20 registros por página, máximo 100.
    Usada en listados de pacientes, análisis y registros ETL.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response(
            {
                "status": "success",
                "pagination": {
                    "count": self.page.paginator.count,
                    "total_pages": self.page.paginator.num_pages,
                    "current_page": self.page.number,
                    "page_size": self.get_page_size(self.request),
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "pagination": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer"},
                        "total_pages": {"type": "integer"},
                        "current_page": {"type": "integer"},
                        "page_size": {"type": "integer"},
                        "next": {"type": "string", "nullable": True},
                        "previous": {"type": "string", "nullable": True},
                    },
                },
                "results": schema,
            },
        }


class LargePagination(PageNumberPagination):
    """
    Paginación para conjuntos grandes de datos: 100 registros por página, máximo 500.
    Usada en exportaciones, reportes y vistas analíticas agregadas.
    """

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 500
    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response(
            {
                "status": "success",
                "pagination": {
                    "count": self.page.paginator.count,
                    "total_pages": self.page.paginator.num_pages,
                    "current_page": self.page.number,
                    "page_size": self.get_page_size(self.request),
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "results": data,
            }
        )


class NoPagination(PageNumberPagination):
    """
    Sin paginación — retorna todos los registros.
    Usar con precaución, solo en endpoints con datasets pequeños y controlados.
    """

    page_size = None

    def paginate_queryset(self, queryset, request, view=None):
        # Desactiva la paginación retornando None
        return None

    def get_paginated_response(self, data):
        return Response({"status": "success", "results": data})