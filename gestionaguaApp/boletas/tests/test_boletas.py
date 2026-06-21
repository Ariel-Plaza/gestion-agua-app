import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from socios.models import Ruta, Socio, Medidor
from lecturas.models import Lectura
from boletas.models import Tarifa, Cobro, Pago
from datetime import date

User = get_user_model()


# ─── TARIFA ───────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_crear_tarifa():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    client.force_authenticate(user=user)

    response = client.post('/boletas/tarifas/agregar/', {
        'cargo_fijo': 6000,
        'precio_m3': 1000,
        'costo_corte_reposicion': 50000,
        'vigente_desde': '2025-01-01',
        'activo': True
    })
    assert response.status_code == 201


@pytest.mark.django_db
def test_listar_tarifas():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    client.force_authenticate(user=user)

    Tarifa.objects.create(
        cargo_fijo=6000, precio_m3=1000, costo_corte_reposicion=50000,
        vigente_desde=date(2025, 1, 1), activo=True
    )
    response = client.get('/boletas/tarifas/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_mostrar_tarifa_por_anno():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    client.force_authenticate(user=user)

    Tarifa.objects.create(
        cargo_fijo=6000, precio_m3=1000, costo_corte_reposicion=50000,
        vigente_desde=date(2025, 1, 1), activo=True
    )
    response = client.get('/boletas/tarifas/2025/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_mostrar_tarifa_anno_inexistente():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    client.force_authenticate(user=user)

    response = client.get('/boletas/tarifas/1900/')
    assert response.status_code == 404


@pytest.mark.django_db
def test_actualizar_tarifa_sin_cobros():
    client = APIClient()
    # rol='administrador' para pasar el check en la vista
    user = User.objects.create_user(username='admin', password='admin123')
    user.rol = 'administrador'
    user.save()
    client.force_authenticate(user=user)

    tarifa = Tarifa.objects.create(
        cargo_fijo=6000, precio_m3=1000, costo_corte_reposicion=50000,
        vigente_desde=date(2025, 1, 1), activo=True
    )
    response = client.patch(f'/boletas/tarifas/actualizar/{tarifa.pk}/', {'precio_m3': 1500})
    assert response.status_code == 200


@pytest.mark.django_db
def test_actualizar_tarifa_con_cobros_bloqueado():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    user.rol = 'administrador'
    user.save()
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
    Cobro.objects.create(
        socio=socio, lectura=lectura, tarifa=tarifa, periodo='2025-01',
        cargo_fijo=6000, costo_m3_consumido=20000, total=26000,
        fecha_vencimiento=date(2025, 2, 28)
    )
    response = client.patch(f'/boletas/tarifas/actualizar/{tarifa.pk}/', {'precio_m3': 1500})
    assert response.status_code == 400


@pytest.mark.django_db
def test_eliminar_tarifa():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    client.force_authenticate(user=user)

    tarifa = Tarifa.objects.create(
        cargo_fijo=6000, precio_m3=1000, costo_corte_reposicion=50000,
        vigente_desde=date(2025, 1, 1), activo=True
    )
    response = client.delete(f'/boletas/tarifas/eliminar/{tarifa.pk}/')
    assert response.status_code == 200
    tarifa.refresh_from_db()
    assert tarifa.activo is False


# ─── COBRO ────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_generar_cobro():
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
    response = client.post('/boletas/cobros/', {
        'socio': socio.pk,
        'lectura': lectura.pk,
        'tarifa': tarifa.pk,
        'periodo': '2025-01',
        'cargo_fijo': 6000,
        'costo_m3_consumido': 20000,
        'fecha_vencimiento': '2025-02-28'
    })
    assert response.status_code == 201
    assert response.data['total'] == 26000


@pytest.mark.django_db
def test_cobro_duplicado_bloqueado():
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
    Cobro.objects.create(
        socio=socio, lectura=lectura, tarifa=tarifa, periodo='2025-01',
        cargo_fijo=6000, costo_m3_consumido=20000, total=26000,
        fecha_vencimiento=date(2025, 2, 28)
    )
    response = client.post('/boletas/cobros/', {
        'socio': socio.pk,
        'lectura': lectura.pk,
        'tarifa': tarifa.pk,
        'periodo': '2025-01',
        'cargo_fijo': 6000,
        'costo_m3_consumido': 20000,
        'fecha_vencimiento': '2025-02-28'
    })
    assert response.status_code == 400


@pytest.mark.django_db
def test_listar_cobros_por_socio():
    client = APIClient()
    user = User.objects.create_user(username='admin', password='admin123')
    client.force_authenticate(user=user)

    ruta = Ruta.objects.create(codigo='R01')
    socio = Socio.objects.create(
        numero_socio=1, rut='12345678-9', nombre='Juan', apellido='Pérez',
        ruta_id=ruta, referencia_direccion='Casa azul', activo=True
    )
    response = client.get(f'/boletas/cobros/socio/{socio.rut}/')
    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_detalle_cobro():
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
    response = client.get(f'/boletas/cobros/{cobro.pk}/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_estado_cobro_pendiente():
    user = User.objects.create_user(username='admin', password='admin123')
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
        fecha_vencimiento=date(2099, 12, 31)
    )
    assert cobro.estado == 'pendiente'


@pytest.mark.django_db
def test_estado_cobro_vencido():
    user = User.objects.create_user(username='admin', password='admin123')
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
        fecha_vencimiento=date(2024, 1, 1)
    )
    assert cobro.estado == 'vencido'


@pytest.mark.django_db
def test_estado_cobro_pagado():
    user = User.objects.create_user(username='admin', password='admin123')
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
        fecha_vencimiento=date(2099, 12, 31)
    )
    Pago.objects.create(cobro=cobro, monto_pagado=26000, forma_pago='efectivo', fecha_pago=date(2025, 2, 1))
    assert cobro.estado == 'pagado'


# ─── PAGO ─────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
def test_registrar_pago():
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
    response = client.post('/boletas/pagos/', {
        'cobro': cobro.pk,
        'monto_pagado': 10000,
        'forma_pago': 'efectivo',
        'fecha_pago': '2025-02-01'
    })
    assert response.status_code == 201


@pytest.mark.django_db
def test_listar_pagos_por_cobro():
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
    response = client.get(f'/boletas/pagos/cobro/{cobro.pk}/')
    assert response.status_code == 200
    assert response.data == []


@pytest.mark.django_db
def test_saldo_pendiente_con_abono():
    user = User.objects.create_user(username='admin', password='admin123')
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
    Pago.objects.create(cobro=cobro, monto_pagado=10000, forma_pago='efectivo', fecha_pago=date(2025, 2, 1))
    assert cobro.saldo_pendiente == 16000


@pytest.mark.django_db
def test_total_pagado():
    user = User.objects.create_user(username='admin', password='admin123')
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
    Pago.objects.create(cobro=cobro, monto_pagado=10000, forma_pago='efectivo', fecha_pago=date(2025, 2, 1))
    assert cobro.total_pagado == 10000