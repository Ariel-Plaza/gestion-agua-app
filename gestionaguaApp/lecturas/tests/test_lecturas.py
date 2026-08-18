import pytest
from rest_framework.test import APIClient
from socios.models import Ruta, Socio, Medidor
from lecturas.models import Lectura
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

# Test creación lectura

@pytest.mark.django_db
def test_create_lectura():
    client = APIClient()
    
    user = User.objects.create_user(username='test', password='test1234')
    user.rol = 'administrador'
    user.save()
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

@pytest.mark.django_db
def test_actualizar_lectura():
    client = APIClient()
    
    user = User.objects.create_user(username='test', password='test1234')
    user.rol = 'administrador'
    user.save()
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
    
    lectura = Lectura.objects.create(
        
            medidor= medidor,
            periodo= "2025-05",
            lectura_actual= 123.45,
            origen= "socio",
            entregado_por= "Juan Perez",
            registrado_por=user,
    )
    
    response = client.patch(
        f"/lecturas/actualizar/{lectura.pk}/",
        format="json",
        data={
            "lectura_actual": "200"
        },
    )
    
    assert response.status_code == 200, response.data
    lectura.refresh_from_db()
    assert lectura.lectura_actual == 200


@pytest.mark.django_db
def test_obtener_lectura_socio_ajeno_bloqueado():
    client = APIClient()

    admin = User.objects.create_user(username='admin', password='admin123')
    admin.rol = 'administrador'
    admin.save()

    ruta = Ruta.objects.create(codigo='AP005')
    dueño = Socio.objects.create(
        numero_socio=1, rut='11111111-1', nombre='usuarioTest', apellido='test',
        ruta_id=ruta, referencia_direccion='calle 2', activo=True,
    )
    otro_socio = Socio.objects.create(
        numero_socio=2, rut='22222222-2', nombre='Ana', apellido='Soto',
        ruta_id=ruta, referencia_direccion='calle 3', activo=True,
    )
    medidor = Medidor.objects.create(
        socio_id=dueño, numero_medidor='M001', estado_servicio='activo',
        fecha_instalacion=date(2024, 1, 1),
    )
    lectura = Lectura.objects.create(
        medidor=medidor, periodo='2025-05', lectura_actual=123.45,
        origen='socio', entregado_por='Juan Perez', registrado_por=admin,
    )

    intruso = User.objects.create_user(username='intruso', password='test1234')
    intruso.rol = 'socio'
    intruso.socio = otro_socio
    intruso.save()
    client.force_authenticate(user=intruso)

    response = client.get(f'/lecturas/buscar/{lectura.pk}/')
    assert response.status_code == 403


@pytest.mark.django_db
def test_obtener_lectura_socio_sin_vinculo_bloqueado():
    # Usuario con rol='socio' pero sin Socio vinculado: debe recibir 403 limpio,
    # no un error 500 al acceder a request.user.socio
    client = APIClient()

    admin = User.objects.create_user(username='admin', password='admin123')
    admin.rol = 'administrador'
    admin.save()

    ruta = Ruta.objects.create(codigo='AP005')
    socio = Socio.objects.create(
        numero_socio=1, rut='11111111-1', nombre='usuarioTest', apellido='test',
        ruta_id=ruta, referencia_direccion='calle 2', activo=True,
    )
    medidor = Medidor.objects.create(
        socio_id=socio, numero_medidor='M001', estado_servicio='activo',
        fecha_instalacion=date(2024, 1, 1),
    )
    lectura = Lectura.objects.create(
        medidor=medidor, periodo='2025-05', lectura_actual=123.45,
        origen='socio', entregado_por='Juan Perez', registrado_por=admin,
    )

    sin_vinculo = User.objects.create_user(username='sin_vinculo', password='test1234')
    sin_vinculo.rol = 'socio'
    sin_vinculo.save()
    client.force_authenticate(user=sin_vinculo)

    response = client.get(f'/lecturas/buscar/{lectura.pk}/')
    assert response.status_code == 403
    assert response.data == {'error': 'Tu usuario no está vinculado a un socio'}