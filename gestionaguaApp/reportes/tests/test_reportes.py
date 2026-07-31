import pytest
from datetime import date
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from socios.models import Ruta, Socio, Medidor
from lecturas.models import Lectura
from boletas.models import Tarifa, Cobro, Pago
from cortes.models import Cortes
from reportes.views import calcular_deudores

User = get_user_model()


def crear_socio(numero_socio, rut, ruta):
    return Socio.objects.create(
        numero_socio=numero_socio, rut=rut, nombre='Test', apellido='Socio',
        ruta_id=ruta, referencia_direccion='Camino real', activo=True
    )


def crear_tarifa():
    return Tarifa.objects.create(
        cargo_fijo=6000, precio_m3=1000, costo_corte_reposicion=50000,
        vigente_desde=date(2025, 1, 1), activo=True
    )


# ─── calcular_deudores() — lógica de selección ─────────────────────────────────

@pytest.mark.django_db
def test_calcular_deudores_incluye_cobro_vencido():
    ruta = Ruta.objects.create(codigo='RD01')
    socio = crear_socio(1, '11111111-1', ruta)
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-RD01', estado_servicio='activo')
    user = User.objects.create_user(username='op1', password='test1234')
    lectura = Lectura.objects.create(
        medidor=medidor, periodo='2025-01', lectura_actual=10,
        m3_consumidos=10, origen='operario', registrado_por=user
    )
    tarifa = crear_tarifa()
    Cobro.objects.create(
        socio=socio, lectura=lectura, tarifa=tarifa, periodo='2025-01',
        cargo_fijo=6000, costo_m3_consumido=10000, total=16000,
        fecha_vencimiento=date(2024, 1, 1),  # ya vencido
    )

    filas, total_adeudado = calcular_deudores()

    assert len(filas) == 1
    assert filas[0]['socio'].pk == socio.pk
    assert filas[0]['saldo'] == 16000
    assert filas[0]['meses_atraso'] == 1
    assert filas[0]['corte_activo'] is False
    assert total_adeudado == 16000


@pytest.mark.django_db
def test_calcular_deudores_incluye_corte_activo_sin_cobro_vencido():
    ruta = Ruta.objects.create(codigo='RD02')
    socio = crear_socio(2, '22222222-2', ruta)
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-RD02', estado_servicio='activo')
    user = User.objects.create_user(username='op2', password='test1234')
    lectura = Lectura.objects.create(
        medidor=medidor, periodo='2025-01', lectura_actual=5,
        m3_consumidos=5, origen='operario', registrado_por=user
    )
    tarifa = crear_tarifa()
    cobro = Cobro.objects.create(
        socio=socio, lectura=lectura, tarifa=tarifa, periodo='2025-01',
        cargo_fijo=6000, costo_m3_consumido=5000, total=11000,
        fecha_vencimiento=date(2099, 12, 31),  # no vencido todavía
    )
    Cortes.objects.create(
        socio=socio, cobro=cobro, fecha_corte=date(2025, 2, 1),
        lectura_corte=5, operador_corte=user, estado='cortado',
    )

    filas, total_adeudado = calcular_deudores()

    assert len(filas) == 1
    assert filas[0]['socio'].pk == socio.pk
    assert filas[0]['corte_activo'] is True
    assert filas[0]['meses_atraso'] == 0


@pytest.mark.django_db
def test_calcular_deudores_excluye_socio_al_dia():
    ruta = Ruta.objects.create(codigo='RD03')
    socio = crear_socio(3, '33333333-3', ruta)
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-RD03', estado_servicio='activo')
    user = User.objects.create_user(username='op3', password='test1234')
    lectura = Lectura.objects.create(
        medidor=medidor, periodo='2025-01', lectura_actual=8,
        m3_consumidos=8, origen='operario', registrado_por=user
    )
    tarifa = crear_tarifa()
    cobro = Cobro.objects.create(
        socio=socio, lectura=lectura, tarifa=tarifa, periodo='2025-01',
        cargo_fijo=6000, costo_m3_consumido=8000, total=14000,
        fecha_vencimiento=date(2099, 12, 31),  # no vencido
    )
    Pago.objects.create(cobro=cobro, monto_pagado=14000, forma_pago='efectivo', fecha_pago=date(2025, 1, 20))

    filas, total_adeudado = calcular_deudores()

    assert filas == []
    assert total_adeudado == 0


# ─── ReporteDeudores — endpoint ─────────────────────────────────────────────────

@pytest.mark.django_db
def test_reporte_deudores_responde_pdf_valido():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    user.rol = 'administrador'
    user.save()
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='RD04')
    socio = crear_socio(4, '44444444-4', ruta)
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-RD04', estado_servicio='activo')
    lectura = Lectura.objects.create(
        medidor=medidor, periodo='2025-01', lectura_actual=10,
        m3_consumidos=10, origen='operario', registrado_por=user
    )
    tarifa = crear_tarifa()
    Cobro.objects.create(
        socio=socio, lectura=lectura, tarifa=tarifa, periodo='2025-01',
        cargo_fijo=6000, costo_m3_consumido=10000, total=16000,
        fecha_vencimiento=date(2024, 1, 1),
    )

    response = client.get('/reportes/deudores/')

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    assert len(response.content) > 0


@pytest.mark.django_db
def test_reporte_deudores_sin_deudores_responde_pdf_valido():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    user.rol = 'administrador'
    user.save()
    client.force_authenticate(user=user)

    response = client.get('/reportes/deudores/')

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    assert len(response.content) > 0


# ─── ReporteRecaudacion — endpoint ───────────────────────────────────────────────

@pytest.mark.django_db
def test_reporte_recaudacion_sin_periodo_responde_400():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    user.rol = 'administrador'
    user.save()
    client.force_authenticate(user=user)

    response = client.get('/reportes/recaudacion/')

    assert response.status_code == 400
    assert 'error' in response.data


@pytest.mark.django_db
def test_reporte_recaudacion_sin_cobros_no_divide_por_cero():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    user.rol = 'administrador'
    user.save()
    client.force_authenticate(user=user)

    response = client.get('/reportes/recaudacion/?periodo=2099-01')

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    assert len(response.content) > 0


@pytest.mark.django_db
def test_reporte_recaudacion_normal_responde_pdf_valido():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    user.rol = 'administrador'
    user.save()
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='RD05')
    socio = crear_socio(5, '55555555-5', ruta)
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-RD05', estado_servicio='activo')
    lectura = Lectura.objects.create(
        medidor=medidor, periodo='2025-01', lectura_actual=10,
        m3_consumidos=10, origen='operario', registrado_por=user
    )
    tarifa = crear_tarifa()
    cobro = Cobro.objects.create(
        socio=socio, lectura=lectura, tarifa=tarifa, periodo='2025-01',
        cargo_fijo=6000, costo_m3_consumido=10000, total=16000,
        fecha_vencimiento=date(2025, 2, 28),
    )
    Pago.objects.create(cobro=cobro, monto_pagado=10000, forma_pago='efectivo', fecha_pago=date(2025, 2, 1))

    response = client.get('/reportes/recaudacion/?periodo=2025-01')

    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'
    assert len(response.content) > 0
