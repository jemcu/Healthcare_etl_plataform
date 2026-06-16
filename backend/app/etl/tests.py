from django.test import TestCase

import pandas as pd
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from authentication.models import CustomUser, Role
from .models import ETLLog
from .services.transformer import transform, _calcular_imc, _clasificar_riesgo


class TransformerUnitTests(TestCase):
    """Tests unitarios de las funciones de transformación."""

    def test_calcular_imc_normal(self):
        imc = _calcular_imc(70, 1.75)
        self.assertAlmostEqual(imc, 22.86, places=1)

    def test_calcular_imc_altura_cero(self):
        imc = _calcular_imc(70, 0)
        self.assertIsNone(imc)

    def test_clasificar_riesgo_critico(self):
        row = {
            'presion_sistolica': 190, 'glucosa': 350,
            'saturacion_oxigeno': 82, 'imc': 35,
            'fumador': True, 'consumo_alcohol': True,
            'antecedentes_familiares': True, 'edad': 70,
        }
        self.assertEqual(_clasificar_riesgo(row), 'Crítico')

    def test_clasificar_riesgo_bajo(self):
        row = {
            'presion_sistolica': 115, 'glucosa': 90,
            'saturacion_oxigeno': 98, 'imc': 22,
            'fumador': False, 'consumo_alcohol': False,
            'antecedentes_familiares': False, 'edad': 30,
        }
        self.assertEqual(_clasificar_riesgo(row), 'Bajo')

    def test_transform_pipeline(self):
        data = {
            'id_paciente':         [1, 2, 2],           # duplicado en id=2
            'nombres':             ['Juan', 'Ana', 'Ana'],
            'apellidos':           ['Pérez', 'García', 'García'],
            'edad':                [45, 'Treinta', 60],  # error de tipo
            'sexo':                ['m', 'f', 'f'],
            'peso':                [80, 60, 60],
            'altura':              [1.75, 1.60, 1.60],
            'imc':                 [None, None, None],
            'presion_sistolica':   [120, 130, 130],
            'presion_diastolica':  [80, 85, 85],
            'frecuencia_cardiaca': [72, 68, 68],
            'glucosa':             [95, None, None],     # nulo
            'colesterol':          [180, 200, 200],
            'saturacion_oxigeno':  [98, 97, 97],
            'temperatura':         [36.5, 37.0, 37.0],
            'antecedentes_familiares': [False, True, True],
            'fumador':             ['si', 'no', 'no'],
            'consumo_alcohol':     [False, False, False],
            'actividad_fisica':    ['moderado', 'leve', 'leve'],
            'diagnostico_preliminar': ['hipertencion', 'normal', 'normal'],
            'fecha_consulta':      ['2024-01-15', '2024-02-10', '2024-02-10'],
        }
        df = pd.DataFrame(data)
        result = transform(df)

        df_clean = result['df_clean']
        stats = result['stats']

        # El duplicado debe haberse removido
        self.assertEqual(stats['duplicados_removidos'], 1)
        self.assertEqual(len(df_clean), 2)

        # El IMC debe estar calculado
        self.assertFalse(df_clean['imc'].isna().any())

        # El diagnóstico debe estar normalizado
        self.assertIn('Hipertensión', df_clean['diagnostico_preliminar'].values)

        # El sexo debe estar normalizado
        self.assertIn('Masculino', df_clean['sexo'].values)


class ETLAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = CustomUser.objects.create_user(
            username='admin_etl',
            password='Admin1234!',
            rol=Role.ADMINISTRADOR,
        )
        self.client.force_authenticate(user=self.admin)

    def test_etl_history_vacio(self):
        response = self.client.get(reverse('etl-history'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 0)

    def test_etl_status_sin_ejecuciones(self):
        response = self.client.get(reverse('etl-status'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_etl_sin_autenticar(self):
        client_anon = APIClient()
        response = client_anon.post(reverse('etl-run'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)