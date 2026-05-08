from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from usuarios.models import Usuario


class AutenticacionTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            password='testpass123',
            rol='administrador'
        )
        self.url_token = reverse('token_obtain_pair')
        self.url_refresh = reverse('token_refresh')
        self.url_blacklist = reverse('token_blacklist')

    # Login
    def test_login_credenciales_correctas(self):
        response = self.client.post(self.url_token, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_credenciales_incorrectas(self):
        response = self.client.post(self.url_token, {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # Payload
    def test_payload_contiene_rol(self):
        import jwt
        response = self.client.post(self.url_token, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        access_token = response.data['access']
        payload = jwt.decode(access_token, options={"verify_signature": False})
        self.assertEqual(payload['rol'], 'administrador')

    # Refresh
    def test_refresh_token_valido(self):
        response = self.client.post(self.url_token, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        refresh_token = response.data['refresh']
        response_refresh = self.client.post(self.url_refresh, {
            'refresh': refresh_token
        })
        self.assertEqual(response_refresh.status_code, status.HTTP_200_OK)
        self.assertIn('access', response_refresh.data)

    # Blacklist
    def test_blacklist_invalida_refresh_token(self):
        response = self.client.post(self.url_token, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        refresh_token = response.data['refresh']

        self.client.post(self.url_blacklist, {'refresh': refresh_token})

        response_refresh = self.client.post(self.url_refresh, {
            'refresh': refresh_token
        })
        self.assertEqual(response_refresh.status_code, status.HTTP_401_UNAUTHORIZED)

    # Endpoints protegidos
    def test_endpoint_protegido_sin_token(self):
        response = self.client.get(reverse('lista-socios'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_endpoint_protegido_con_token(self):
        response = self.client.post(self.url_token, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(reverse('lista-socios'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)