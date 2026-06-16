import numpy as np
import pandas as pd
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status


from authentication.models import CustomUser, Role
from .services.preprocessor import preprocess, FEATURE_COLUMNS, RIESGO_ENCODING
from .services.evaluator import evaluar_modelo
from .services.predictor import predecir_riesgo


def _make_dummy_df(n=200):
    """Genera un DataFrame clínico sintético para tests."""
    np.random.seed(42)
    data = {
        'edad': np.random.randint(18, 85, n),
        'peso': np.random.uniform(50, 110, n),
        'altura': np.random.uniform(1.50, 1.90, n),
        'imc': np.random.uniform(18, 40, n),
        'presion_sistolica': np.random.randint(90, 185, n),
        'presion_diastolica': np.random.randint(60, 120, n),
        'frecuencia_cardiaca': np.random.randint(55, 110, n),
        'glucosa': np.random.uniform(70, 310, n),
        'colesterol': np.random.uniform(100, 350, n),
        'saturacion_oxigeno': np.random.uniform(88, 100, n),
        'temperatura': np.random.uniform(35.5, 39.5, n),
        'fumador': np.random.randint(0, 2, n),
        'consumo_alcohol': np.random.randint(0, 2, n),
        'antecedentes_familiares': np.random.randint(0, 2, n),
        'riesgo_enfermedad': np.random.choice(['Bajo', 'Medio', 'Alto', 'Crítico'], n),
    }
    return pd.DataFrame(data)


class PreprocessorTests(TestCase):
    def test_preprocess_shapes(self):
        df = _make_dummy_df(200)
        result = preprocess(df)
        X, y = result['X'], result['y']
        self.assertEqual(X.shape[1], len(FEATURE_COLUMNS))
        self.assertEqual(len(X), len(y))

    def test_preprocess_encoding(self):
        df = _make_dummy_df(100)
        result = preprocess(df)
        clases = set(result['y'])
        for c in clases:
            self.assertIn(c, RIESGO_ENCODING.values())


class EvaluatorTests(TestCase):
    def test_metricas_presentes(self):
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler

        df = _make_dummy_df(300)
        result = preprocess(df)
        X, y = result['X'], result['y']

        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('model', RandomForestClassifier(n_estimators=10, random_state=42)),
        ])
        pipeline.fit(X, y)

        metricas = evaluar_modelo(pipeline, X, y)

        for key in ['accuracy', 'precision', 'recall', 'f1_score', 'matriz_confusion']:
            self.assertIn(key, metricas)

        self.assertGreaterEqual(metricas['accuracy'], 0)
        self.assertLessEqual(metricas['accuracy'], 1)


class MLAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = CustomUser.objects.create_user(
            username='admin_ml',
            password='Admin1234!',
            rol=Role.ADMINISTRADOR,
        )
        self.client.force_authenticate(user=self.admin)

    def test_list_models_vacio(self):
        response = self.client.get(reverse('ml-models-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total'], 0)

    def test_metrics_sin_modelo_activo(self):
        response = self.client.get(reverse('ml-metrics'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_predict_sin_modelo(self):
        datos = {
            'edad': 55, 'peso': 90, 'altura': 1.70,
            'presion_sistolica': 145, 'presion_diastolica': 95,
            'frecuencia_cardiaca': 88, 'glucosa': 140,
            'colesterol': 220, 'saturacion_oxigeno': 96,
            'temperatura': 37.0, 'fumador': True,
            'consumo_alcohol': False, 'antecedentes_familiares': True,
        }
        response = self.client.post(reverse('ml-predict'), datos, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sin_autenticar(self):
        anon = APIClient()
        response = anon.post(reverse('ml-train'), {'algoritmo': 'random_forest'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)