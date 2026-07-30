import pytest
from unittest.mock import patch
from rest_framework.test import APIClient
from socios.models import Ruta, Socio
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_lista_socios_responde_200_normal():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='LS01')
    Socio.objects.create(
        numero_socio=1, rut='11111111-1', nombre='Juan', apellido='Pérez',
        ruta_id=ruta, referencia_direccion='Casa azul', activo=True
    )

    response = client.get('/socios/')
    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_lista_socios_error_interno_responde_500():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    with patch('socios.views.Socio.objects.exclude', side_effect=Exception('fallo de conexión')):
        response = client.get('/socios/')

    assert response.status_code == 500
    assert response.data == {'error': 'No se pudo obtener el listado de socios'}
