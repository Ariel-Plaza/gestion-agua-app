import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from socios.models import Ruta, Socio, Medidor
from lecturas.models import Lectura
from boletas.models import Tarifa, Cobro
from datetime import date

User = get_user_model()


@pytest.mark.django_db
def test_cupon_responde_pdf_valido():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='C01')
    socio = Socio.objects.create(
        numero_socio=1, rut='12345678-5', nombre='Juan', apellido='Pérez',
        ruta_id=ruta, referencia_direccion='Casa azul', activo=True
    )
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-C01', estado_servicio='activo')
    lectura = Lectura.objects.create(
        medidor=medidor, periodo='2025-01', lectura_actual=100,
        m3_consumidos=20, origen='operario', registrado_por=user
    )
    tarifa = Tarifa.objects.create(
        cargo_fijo=6000, precio_m3=1000, costo_corte_reposicion=50000,
        vigente_desde=date(2025, 1, 1), activo=True
    )
    cobro = Cobro.objects.create(
        socio=socio, lectura=lectura, tarifa=tarifa, periodo='2025-01',
        cargo_fijo=6000, costo_m3_consumido=20000, total=26000,
        numero_boleta='2025-00001', fecha_vencimiento=date(2025, 2, 28)
    )

    response = client.get(f'/boletas/cobros/{cobro.pk}/cupon/')

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    assert len(response.content) > 0


@pytest.mark.django_db
def test_cupon_cobro_con_reposicion():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='C02')
    socio = Socio.objects.create(
        numero_socio=2, rut='22222222-2', nombre='Ana', apellido='Soto',
        ruta_id=ruta, referencia_direccion='Camino real', activo=True
    )
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-C02', estado_servicio='activo')
    lectura = Lectura.objects.create(
        medidor=medidor, periodo='2025-02', lectura_actual=10,
        m3_consumidos=10, origen='operario', registrado_por=user
    )
    tarifa = Tarifa.objects.create(
        cargo_fijo=6000, precio_m3=1000, costo_corte_reposicion=50000,
        vigente_desde=date(2025, 1, 1), activo=True
    )
    cobro = Cobro.objects.create(
        socio=socio, lectura=lectura, tarifa=tarifa, periodo='2025-02',
        cargo_fijo=6000, costo_m3_consumido=10000, corte_reposicion=50000,
        total=66000, numero_boleta='2025-00002', fecha_vencimiento=date(2025, 3, 31)
    )

    response = client.get(f'/boletas/cobros/{cobro.pk}/cupon/')

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    assert len(response.content) > 0


@pytest.mark.django_db
def test_cupon_cobro_inexistente():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    client.force_authenticate(user=user)

    response = client.get('/boletas/cobros/99999/cupon/')
    assert response.status_code == 404
