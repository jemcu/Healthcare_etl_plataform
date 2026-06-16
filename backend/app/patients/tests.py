from django.test import TestCase

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from authentication.models import CustomUser, Role
from .models import Paciente
from .services.transformer import calcular_imc, clasificar_imc, clasificar_riesgo, enriquecer_paciente
from .services.loader import crear_paciente, recalcular_todos_los_riesgos


PACIENTE_BASE = {
    'nombres': 'Carlos',
    'apellidos': 'Gómez',
    'edad': 45,
    'sexo': 'Masculino',
    'peso': 85.0,
    'altura': 1.72,
    'presion_sistolica': 135,
    'presion_diastolica': 88,
    'frecuencia_cardiaca': 78,
    'glucosa': 105.0,
    'colesterol': 210.0,
    'saturacion_oxigeno': 97.0,
    'temperatura': 36.8,
    'antecedentes_familiares': True,
    'fumador': False,
    'consumo_alcohol': False,
    'actividad_fisica': 'Moderado',
    'diagnostico_preliminar': 'Hipertensión',
    'fecha_consulta': '2024-06-01',
}


# ── Unit tests ────────────────────────────────────────────────────────────────

class TransformerUnitTests(TestCase):

    def test_calcular_imc_correcto(self):
        imc = calcular_imc(85, 1.72)
        self.assertAlmostEqual(imc, 28.74, places=1)

    def test_calcular_imc_altura_cero(self):
        self.assertEqual(calcular_imc(70, 0), 0.0)

    def test_clasificar_imc(self):
        self.assertEqual(clasificar_imc(17.0), 'Bajo peso')
        self.assertEqual(clasificar_imc(22.0), 'Normal')
        self.assertEqual(clasificar_imc(27.0), 'Sobrepeso')
        self.assertEqual(clasificar_imc(32.0), 'Obesidad I')

    def test_clasificar_riesgo_critico(self):
        data = {
            'presion_sistolica': 195, 'glucosa': 320,
            'saturacion_oxigeno': 82, 'imc': 38,
            'fumador': True, 'consumo_alcohol': True,
            'antecedentes_familiares': True, 'edad': 72,
        }
        self.assertEqual(clasificar_riesgo(data), 'Crítico')

    def test_clasificar_riesgo_bajo(self):
        data = {
            'presion_sistolica': 110, 'glucosa': 85,
            'saturacion_oxigeno': 99, 'imc': 22,
            'fumador': False, 'consumo_alcohol': False,
            'antecedentes_familiares': False, 'edad': 28,
        }
        self.assertEqual(clasificar_riesgo(data), 'Bajo')

    def test_enriquecer_paciente_agrega_imc_y_riesgo(self):
        data = {'peso': 90, 'altura': 1.75, 'presion_sistolica': 120,
                'glucosa': 95, 'saturacion_oxigeno': 98, 'imc': 0,
                'fumador': False, 'consumo_alcohol': False,
                'antecedentes_familiares': False, 'edad': 35}
        result = enriquecer_paciente(data)
        self.assertGreater(result['imc'], 0)
        self.assertIn(result['riesgo_enfermedad'], ['Bajo', 'Medio', 'Alto', 'Crítico'])


# ── Model tests ───────────────────────────────────────────────────────────────

class PacienteModelTests(TestCase):

    def setUp(self):
        self.paciente = crear_paciente(dict(PACIENTE_BASE))

    def test_nombre_completo(self):
        self.assertEqual(self.paciente.nombre_completo, 'Carlos Gómez')

    def test_imc_calculado(self):
        self.assertGreater(self.paciente.imc, 0)

    def test_riesgo_asignado(self):
        self.assertIn(self.paciente.riesgo_enfermedad, ['Bajo', 'Medio', 'Alto', 'Crítico'])

    def test_es_critico_false(self):
        # Valores normales → no crítico
        self.assertFalse(self.paciente.es_critico)

    def test_recalcular_riesgos(self):
        count = recalcular_todos_los_riesgos()
        self.assertEqual(count, 1)


# ── API tests ─────────────────────────────────────────────────────────────────

class PacienteAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.medico = CustomUser.objects.create_user(
            username='medico_test',
            password='Medico1234!',
            rol=Role.MEDICO,
        )
        self.client.force_authenticate(user=self.medico)

    def test_listar_pacientes_vacio(self):
        response = self.client.get(reverse('pacientes-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 0)

    def test_crear_paciente(self):
        response = self.client.post(
            reverse('pacientes-list'),
            PACIENTE_BASE,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('imc', response.data)
        self.assertIn('riesgo_enfermedad', response.data)

    def test_detalle_paciente(self):
        paciente = crear_paciente(dict(PACIENTE_BASE))
        response = self.client.get(reverse('pacientes-detail', args=[paciente.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombres'], 'Carlos')

    def test_eliminar_paciente(self):
        paciente = crear_paciente(dict(PACIENTE_BASE))
        response = self.client.delete(reverse('pacientes-detail', args=[paciente.pk]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Paciente.objects.filter(pk=paciente.pk).exists())

    def test_stats(self):
        crear_paciente(dict(PACIENTE_BASE))
        response = self.client.get(reverse('pacientes-stats'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 1)

    def test_sin_autenticar(self):
        anon = APIClient()
        response = anon.get(reverse('pacientes-list'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)