from django.test import TestCase

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import CustomUser, Role


class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Crear usuario administrador de prueba
        self.admin = CustomUser.objects.create_user(
            username='admin_test',
            password='Admin1234!',
            email='admin@test.com',
            first_name='Admin',
            last_name='Test',
            rol=Role.ADMINISTRADOR,
        )

        # Crear usuario médico de prueba
        self.medico = CustomUser.objects.create_user(
            username='medico_test',
            password='Medico1234!',
            email='medico@test.com',
            rol=Role.MEDICO,
        )

    # ── Login ──────────────────────────────────────────────────────────────
    def test_login_exitoso(self):
        response = self.client.post(reverse('auth-login'), {
            'username': 'admin_test',
            'password': 'Admin1234!',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['rol'], Role.ADMINISTRADOR)

    def test_login_credenciales_invalidas(self):
        response = self.client.post(reverse('auth-login'), {
            'username': 'admin_test',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Me ─────────────────────────────────────────────────────────────────
    def test_me_autenticado(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(reverse('auth-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'admin_test')

    def test_me_sin_autenticar(self):
        response = self.client.get(reverse('auth-me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ── Register ───────────────────────────────────────────────────────────
    def test_registro_solo_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(reverse('auth-register'), {
            'username': 'nuevo_user',
            'email': 'nuevo@test.com',
            'first_name': 'Nuevo',
            'last_name': 'Usuario',
            'rol': Role.ANALISTA,
            'password': 'Nuevo1234!',
            'password2': 'Nuevo1234!',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_registro_medico_denegado(self):
        self.client.force_authenticate(user=self.medico)
        response = self.client.post(reverse('auth-register'), {
            'username': 'otro_user',
            'password': 'Otro1234!',
            'password2': 'Otro1234!',
            'rol': Role.ANALISTA,
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ── Roles ──────────────────────────────────────────────────────────────
    def test_propiedades_rol(self):
        self.assertTrue(self.admin.is_administrador)
        self.assertFalse(self.admin.is_medico)
        self.assertTrue(self.medico.is_medico)
        self.assertFalse(self.medico.is_administrador)