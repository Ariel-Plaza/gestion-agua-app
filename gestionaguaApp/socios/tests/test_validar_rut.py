import pytest
from rest_framework.test import APIClient
from socios.models import Ruta, Socio, Medidor
from socios.views import validar_rut, normalizar_rut
from django.contrib.auth import get_user_model

User = get_user_model()


# ─── validar_rut() — unitarios ─────────────────────────────────────────────────

def test_validar_rut_con_dv_correcto():
    assert validar_rut('12345678-5') is True


def test_validar_rut_con_dv_incorrecto():
    assert validar_rut('12345678-9') is False


def test_validar_rut_normaliza_antes_de_validar():
    assert validar_rut(normalizar_rut('12.345.678-5')) is True


def test_validar_rut_sin_guion():
    assert validar_rut('123456785') is False


def test_validar_rut_cuerpo_no_numerico():
    assert validar_rut('abcdefgh-5') is False


# ─── ObtenerSocioNombreApellidos (buscar por rut) ──────────────────────────────

@pytest.mark.django_db
def test_buscar_socio_rut_valido():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='V01')
    Socio.objects.create(
        numero_socio=1, rut='12345678-5', nombre='Juan', apellido='Pérez',
        ruta_id=ruta, referencia_direccion='Casa azul', activo=True
    )
    response = client.get('/socios/buscar/?rut=12345678-5')
    assert response.status_code == 200


@pytest.mark.django_db
def test_buscar_socio_rut_invalido():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    response = client.get('/socios/buscar/?rut=12345678-9')
    assert response.status_code == 400


# ─── AgregarSocio ───────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_agregar_socio_rut_valido():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    Ruta.objects.create(codigo='V02')
    response = client.post('/socios/agregar/', format='json', data={
        'numero_socio': 2, 'rut': '12.345.678-5', 'nombre': 'Ana', 'apellido': 'Soto',
        'ruta_id': 'V02', 'referencia_direccion': 'Camino real',
    })
    assert response.status_code == 201, response.data
    assert response.data['rut'] == '12345678-5'


@pytest.mark.django_db
def test_agregar_socio_rut_invalido():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    Ruta.objects.create(codigo='V03')
    response = client.post('/socios/agregar/', format='json', data={
        'numero_socio': 3, 'rut': '12345678-9', 'nombre': 'Ana', 'apellido': 'Soto',
        'ruta_id': 'V03', 'referencia_direccion': 'Camino real',
    })
    assert response.status_code == 400


# ─── ActualizarSocio ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_actualizar_socio_rut_valido():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='V04')
    socio = Socio.objects.create(
        numero_socio=4, rut='11111111-1', nombre='Luis', apellido='Rojas',
        ruta_id=ruta, referencia_direccion='Camino real', activo=True
    )
    response = client.put(f'/socios/actualizar/{socio.pk}/', format='json', data={
        'rut': '12.345.678-5',
    })
    assert response.status_code == 200, response.data
    assert response.data['rut'] == '12345678-5'


@pytest.mark.django_db
def test_actualizar_socio_rut_invalido():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='V05')
    socio = Socio.objects.create(
        numero_socio=5, rut='11111111-1', nombre='Eva', apellido='Vera',
        ruta_id=ruta, referencia_direccion='Camino real', activo=True
    )
    response = client.put(f'/socios/actualizar/{socio.pk}/', format='json', data={
        'rut': '12345678-9',
    })
    assert response.status_code == 400


@pytest.mark.django_db
def test_actualizar_socio_sin_rut_no_dispara_validacion():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='V06')
    socio = Socio.objects.create(
        numero_socio=6, rut='11111111-1', nombre='Marta', apellido='Diaz',
        ruta_id=ruta, referencia_direccion='Camino real', activo=True
    )
    response = client.put(f'/socios/actualizar/{socio.pk}/', format='json', data={
        'nombre': 'Marta Editada',
    })
    assert response.status_code == 200, response.data
    assert response.data['rut'] == '11111111-1'
    assert response.data['nombre'] == 'Marta Editada'


# ─── AgregarMedidor ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_agregar_medidor_rut_valido():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='V07')
    socio = Socio.objects.create(
        numero_socio=7, rut='12345678-5', nombre='Carlos', apellido='Diaz',
        ruta_id=ruta, referencia_direccion='Camino real', activo=True
    )
    response = client.post('/socios/medidores/agregar/', format='json', data={
        'numero_medidor': 'MED-V07', 'rut': '12345678-5',
    })
    assert response.status_code == 201, response.data
    assert response.data['socio_id'] == socio.pk


@pytest.mark.django_db
def test_agregar_medidor_rut_invalido():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    response = client.post('/socios/medidores/agregar/', format='json', data={
        'numero_medidor': 'MED-V08', 'rut': '12345678-9',
    })
    assert response.status_code == 400


# ─── ActualizarMedidor ───────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_actualizar_medidor_rut_valido():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='V09')
    socio_original = Socio.objects.create(
        numero_socio=8, rut='11111111-1', nombre='Pedro', apellido='Soto',
        ruta_id=ruta, referencia_direccion='Camino real', activo=True
    )
    socio_nuevo = Socio.objects.create(
        numero_socio=9, rut='12345678-5', nombre='Sofía', apellido='Soto',
        ruta_id=ruta, referencia_direccion='Camino real', activo=True
    )
    medidor = Medidor.objects.create(
        socio_id=socio_original, numero_medidor='MED-V09', estado_servicio='activo'
    )
    response = client.put(f'/socios/medidores/actualizar/{medidor.pk}/', format='json', data={
        'rut': '12345678-5',
    })
    assert response.status_code == 200, response.data
    assert response.data['socio_id'] == socio_nuevo.pk


@pytest.mark.django_db
def test_actualizar_medidor_rut_invalido():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='V10')
    socio = Socio.objects.create(
        numero_socio=10, rut='11111111-1', nombre='Rosa', apellido='Vera',
        ruta_id=ruta, referencia_direccion='Camino real', activo=True
    )
    medidor = Medidor.objects.create(
        socio_id=socio, numero_medidor='MED-V10', estado_servicio='activo'
    )
    response = client.put(f'/socios/medidores/actualizar/{medidor.pk}/', format='json', data={
        'rut': '12345678-9',
    })
    assert response.status_code == 400


# ─── ListaMedidores (filtro por rut) ────────────────────────────────────────────

@pytest.mark.django_db
def test_lista_medidores_rut_valido():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='V11')
    socio = Socio.objects.create(
        numero_socio=11, rut='12345678-5', nombre='Tomás', apellido='Rojas',
        ruta_id=ruta, referencia_direccion='Camino real', activo=True
    )
    Medidor.objects.create(socio_id=socio, numero_medidor='MED-V11', estado_servicio='activo')
    response = client.get('/socios/medidores/?rut=12345678-5')
    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_lista_medidores_rut_invalido():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    response = client.get('/socios/medidores/?rut=12345678-9')
    assert response.status_code == 400
