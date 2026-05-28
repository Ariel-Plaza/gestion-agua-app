import pytest
from rest_framework.test import APIClient
from socios.models import Ruta
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