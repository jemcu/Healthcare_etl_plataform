from django.test import TestCase

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from authentication.models import CustomUser, Role
from patients.services.loader import crear_paciente


PACIENTE_BASE = {
    'nombres': 'Ana', 'apellidos': 'Torres', 'edad': 52, 'sexo': 'Femenino',
    'peso': 72.0, 'altura': 1.62, 'presion_sistolica': 145,
    'presion_diastolica': 92, 'frecuencia_cardiaca': 80,
    'glucosa': 130.0, 'colesterol': 235.0, 'saturacion_oxigeno': 96.0,
    'temperatura': 37.1, 'antecedentes_familiares': True,
    'fumador': False, 'consumo_alcohol': False,
    'actividad_fisica': 'Leve',
    'diagnostico_preliminar': 'Hipertensión',
    'fecha_consulta': '2024-06-01',
}


class ReportesAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = CustomUser.objects.create_user(
            username='admin_rep',
            password='Admin1234!',
            rol=Role.ADMINISTRADOR,
        )
        self.client.force_authenticate(user=self.admin)
        crear_paciente(dict(PACIENTE_BASE))

    # ── Pacientes ─────────────────────────────────────────────────────────

    def test_reporte_pacientes_csv(self):
        response = self.client.get(reverse('reportes-pacientes') + '?formato=csv')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('text/csv', response['Content-Type'])

    def test_reporte_pacientes_excel(self):
        response = self.client.get(reverse('reportes-pacientes') + '?formato=excel')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('spreadsheetml', response['Content-Type'])

    def test_reporte_pacientes_pdf(self):
        response = self.client.get(reverse('reportes-pacientes') + '?formato=pdf')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_reporte_pacientes_formato_invalido(self):
        response = self.client.get(reverse('reportes-pacientes') + '?formato=xml')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Analítica ─────────────────────────────────────────────────────────

    def test_reporte_analitica_pdf(self):
        response = self.client.get(reverse('reportes-analitica') + '?formato=pdf')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reporte_analitica_excel(self):
        response = self.client.get(reverse('reportes-analitica') + '?formato=excel')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ── ETL ───────────────────────────────────────────────────────────────

    def test_reporte_etl_csv(self):
        response = self.client.get(reverse('reportes-etl') + '?formato=csv')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ── Historial ─────────────────────────────────────────────────────────

    def test_historial_reportes(self):
        # Generar uno primero
        self.client.get(reverse('reportes-pacientes') + '?formato=csv')
        response = self.client.get(reverse('reportes-historial'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['total'], 1)

    # ── Autenticación ─────────────────────────────────────────────────────

    def test_sin_autenticar(self):
        anon = APIClient()
        response = anon.get(reverse('reportes-pacientes'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)