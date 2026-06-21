import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from socios.models import Ruta, Socio, Medidor
from lecturas.models import Lectura
from boletas.models import Tarifa, Cobro
from cortes.models import Cortes
from datetime import date

User = get_user_model()


@pytest.mark.django_db
def test_registrar_corte():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='R01')
    socio = Socio.objects.create(
        numero_socio=1, rut='12345678-9', nombre='Juan', apellido='Pérez',
        ruta_id=ruta, referencia_direccion='Casa azul', activo=True
    )
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-001', estado_servicio='activo')
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
        fecha_vencimiento=date(2025, 2, 28)
    )
    response = client.post('/cortes/', {
        'socio': socio.pk,
        'cobro': cobro.pk,
        'fecha_corte': '2025-03-01',
        'lectura_corte': 120,
        'operador_corte': user.pk,
        'estado': 'cortado'
    })
    assert response.status_code == 201
    assert response.data['estado'] == 'cortado'


@pytest.mark.django_db
def test_registrar_reposicion():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='R01')
    socio = Socio.objects.create(
        numero_socio=1, rut='12345678-9', nombre='Juan', apellido='Pérez',
        ruta_id=ruta, referencia_direccion='Casa azul', activo=True
    )
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-001', estado_servicio='activo')
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
        fecha_vencimiento=date(2025, 2, 28)
    )
    corte = Cortes.objects.create(
        socio=socio, cobro=cobro, fecha_corte=date(2025, 3, 1),
        lectura_corte=120, operador_corte=user, estado='cortado'
    )
    response = client.patch(f'/cortes/{corte.pk}/reposicion/', {
        'fecha_reposicion': '2025-03-15',
        'lectura_reposicion': 125
    })
    assert response.status_code == 200
    assert response.data['estado'] == 'repuesto'


@pytest.mark.django_db
def test_reposicion_ya_repuesta():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='R01')
    socio = Socio.objects.create(
        numero_socio=1, rut='12345678-9', nombre='Juan', apellido='Pérez',
        ruta_id=ruta, referencia_direccion='Casa azul', activo=True
    )
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-001', estado_servicio='activo')
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
        fecha_vencimiento=date(2025, 2, 28)
    )
    corte = Cortes.objects.create(
        socio=socio, cobro=cobro, fecha_corte=date(2025, 3, 1),
        lectura_corte=120, operador_corte=user, estado='repuesto'
    )
    response = client.patch(f'/cortes/{corte.pk}/reposicion/', {
        'fecha_reposicion': '2025-03-20',
        'lectura_reposicion': 130
    })
    assert response.status_code == 400


@pytest.mark.django_db
def test_listar_cortes_por_socio():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='R01')
    socio = Socio.objects.create(
        numero_socio=1, rut='12345678-9', nombre='Juan', apellido='Pérez',
        ruta_id=ruta, referencia_direccion='Casa azul', activo=True
    )
    response = client.get(f'/cortes/socio/{socio.rut}/')
    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_detalle_corte():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='R01')
    socio = Socio.objects.create(
        numero_socio=1, rut='12345678-9', nombre='Juan', apellido='Pérez',
        ruta_id=ruta, referencia_direccion='Casa azul', activo=True
    )
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-001', estado_servicio='activo')
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
        fecha_vencimiento=date(2025, 2, 28)
    )
    corte = Cortes.objects.create(
        socio=socio, cobro=cobro, fecha_corte=date(2025, 3, 1),
        lectura_corte=120, operador_corte=user, estado='cortado'
    )
    response = client.get(f'/cortes/{corte.pk}/')
    assert response.status_code == 200