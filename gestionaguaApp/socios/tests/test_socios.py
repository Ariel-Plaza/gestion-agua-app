import pytest
from rest_framework.test import APIClient
from socios.models import Ruta, Socio, Medidor
from django.contrib.auth import get_user_model

User = get_user_model()



# Test creación socio
@pytest.mark.django_db
def test_create_socio():
    client = APIClient()

    # Autenticacion
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    Ruta.objects.create(codigo="AP005")
    response = client.post(
        "/socios/agregar/",
        format="json",
        data=
            {
                "numero_socio" : "1",
                "rut":"11111111-1",
                "nombre":"usuario",
                "apellido":"test",
                "segundo_apellido":"prueba",
                "telefono":"12345679",
                "email":"test@correo.com",
                "ruta_id":"AP005",
                "referencia_direccion":"calle 2",
                "subsidio":"false",
                "activo": "true",
            },
    )
    assert response.status_code == 201, response.data

#Test obtener socio
@pytest.mark.django_db
def test_get_socios():
    client = APIClient()
    # Autenticacion
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)
    
    response = client.get("/socios/")
    assert response.status_code == 200

#Test actualizar socio
@pytest.mark.django_db
def test_update_socio():
    client = APIClient()
    
    # Autenticacion
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)
    
    Ruta.objects.create(codigo="AP002")
    response = client.post(
        "/socios/agregar/",
        format="json",
        data={
            "numero_socio": "2",
            "rut": "22222222-2",
            "nombre": "usuario2",
            "apellido": "test2",
            "segundo_apellido": "prueba2",
            "telefono": "222222222",
            "email": "test2@correo.com",
            "ruta_id": "AP002",
            "referencia_direccion": "calle prueba 2",
            "subsidio": "false",
            "activo": "true",
        },
    )

    socio_id = response.data.get("id") or response.data.get("numero_socio")
    print(f"✓ Socio creado: ID {socio_id}")
    
    response = client.put(
        f"/socios/actualizar/{socio_id}/",
        format="json",
        data={
            "nombre": "usuario_actualizado",
        },
    )
    assert response.status_code == 200

#Test eliminar socio 
@pytest.mark.django_db
def test_delete_socio():
    client = APIClient()
    
    # Autenticacion
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)
    
    Ruta.objects.create(codigo="AP001")
    response = client.post(
        "/socios/agregar/",
        format="json",
        data={
            "numero_socio": "3",
            "rut": "33333333-3",
            "nombre": "usuario3",
            "apellido": "test3",
            "segundo_apellido": "prueba3",
            "telefono": "333333333",
            "email": "test3@correo.com",
            "ruta_id": "AP001",
            "referencia_direccion": "calle prueba 3",
            "subsidio": "false",
            "activo": "true",
        },
    )

    socio_id = response.data.get("id") or response.data.get("numero_socio")
    print(f"✓ Socio creado: ID {socio_id}")

    response = client.delete(
        f"/socios/eliminar/{socio_id}/",
    )
    assert response.status_code == 200


# Test agregar medidor resolviendo rut
@pytest.mark.django_db
def test_agregar_medidor_resuelve_rut():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='AP010')
    socio = Socio.objects.create(
        numero_socio=10, rut='10101010-4', nombre='Ana', apellido='Soto',
        ruta_id=ruta, referencia_direccion='Camino real', activo=True
    )
    response = client.post(
        "/socios/medidores/agregar/",
        format="json",
        data={
            "numero_medidor": "MED-100",
            "rut": "10101010-4",
        },
    )
    assert response.status_code == 201, response.data
    assert response.data["socio_id"] == socio.pk


# Test agregar medidor con rut inexistente
@pytest.mark.django_db
def test_agregar_medidor_rut_inexistente():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    response = client.post(
        "/socios/medidores/agregar/",
        format="json",
        data={
            "numero_medidor": "MED-101",
            "rut": "99999999-9",
        },
    )
    assert response.status_code == 404


# Test reasignar medidor a otro socio por rut (Bug 3)
@pytest.mark.django_db
def test_actualizar_medidor_reasigna_socio_por_rut():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='AP011')
    socio_original = Socio.objects.create(
        numero_socio=11, rut='11111111-9', nombre='Carlos', apellido='Diaz',
        ruta_id=ruta, referencia_direccion='Camino real 2', activo=True
    )
    socio_nuevo = Socio.objects.create(
        numero_socio=12, rut='12121212-9', nombre='Marta', apellido='Diaz',
        ruta_id=ruta, referencia_direccion='Camino real 2', activo=True
    )
    medidor = Medidor.objects.create(
        socio_id=socio_original, numero_medidor='MED-102', estado_servicio='activo'
    )

    response = client.put(
        f"/socios/medidores/actualizar/{medidor.pk}/",
        format="json",
        data={"rut": "12121212-9"},
    )
    assert response.status_code == 200, response.data
    assert response.data["socio_id"] == socio_nuevo.pk


# Test actualizar medidor sin rut no cambia el socio asignado
@pytest.mark.django_db
def test_actualizar_medidor_sin_rut_mantiene_socio():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='AP012')
    socio = Socio.objects.create(
        numero_socio=13, rut='13131313-1', nombre='Luis', apellido='Rojas',
        ruta_id=ruta, referencia_direccion='Camino real 3', activo=True
    )
    medidor = Medidor.objects.create(
        socio_id=socio, numero_medidor='MED-103', estado_servicio='activo'
    )

    response = client.put(
        f"/socios/medidores/actualizar/{medidor.pk}/",
        format="json",
        data={"estado_servicio": "cortado"},
    )
    assert response.status_code == 200, response.data
    assert response.data["socio_id"] == socio.pk
    assert response.data["estado_servicio"] == "cortado"


# Test reasignar medidor con rut inexistente
@pytest.mark.django_db
def test_actualizar_medidor_rut_inexistente():
    client = APIClient()
    user = User.objects.create_user(username='test', password='test1234')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='AP013')
    socio = Socio.objects.create(
        numero_socio=14, rut='14141414-1', nombre='Eva', apellido='Vera',
        ruta_id=ruta, referencia_direccion='Camino real 4', activo=True
    )
    medidor = Medidor.objects.create(
        socio_id=socio, numero_medidor='MED-104', estado_servicio='activo'
    )

    response = client.put(
        f"/socios/medidores/actualizar/{medidor.pk}/",
        format="json",
        data={"rut": "99999999-9"},
    )
    assert response.status_code == 404