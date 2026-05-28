import pytest
from rest_framework.test import APIClient
from socios.models import Ruta, Socio, Medidor
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

# Test creación lectura

@pytest.mark.django_db
def test_create_lectura():
    client = APIClient()
    
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo="AP005")
    socio = Socio.objects.create(
        numero_socio=1,
        rut='11111111-1',
        nombre='usuarioTest',
        apellido='test',
        segundo_apellido='prueba',
        telefono='12345679',
        email='test@correo.com',
        ruta_id=ruta,
        referencia_direccion='calle 2',
        subsidio=False,
        activo=True,
    )
    medidor = Medidor.objects.create(
        socio_id=socio,
        numero_medidor='M001',
        estado_servicio='activo',
        fecha_instalacion=date(2024, 1, 1),
    )

    response = client.post(
        "/lecturas/agregar/",
        format="json",
        data={
            "medidor": medidor.id,
            "periodo": "2025-05",
            "lectura_actual": "123.45",
            "origen": "socio",
            "entregado_por": "Juan Perez",
        },
    )

    assert response.status_code == 201, response.data
    assert response.data["m3_consumidos"] == "0.00"

