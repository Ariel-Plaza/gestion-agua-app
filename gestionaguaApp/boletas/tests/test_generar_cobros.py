import pytest
from datetime import date
from unittest.mock import patch
from django.conf import settings
from django.core import mail
from django.core.management import call_command
from django.contrib.auth import get_user_model
from socios.models import Ruta, Socio, Medidor
from lecturas.models import Lectura
from boletas.models import Tarifa, Cobro, Pago
from cortes.models import Cortes

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


@pytest.mark.django_db
def test_generar_cobros_crea_cobro_basico():
    user = User.objects.create_user(username='operario', password='test1234')
    ruta = Ruta.objects.create(codigo='G01')
    socio = crear_socio(1, '11111111-1', ruta)
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-G01', estado_servicio='activo')
    Lectura.objects.create(
        medidor=medidor, periodo='2024-12', lectura_actual=0,
        m3_consumidos=0, origen='operario', registrado_por=user
    )
    Lectura.objects.create(
        medidor=medidor, periodo='2025-01', lectura_actual=20,
        m3_consumidos=20, origen='operario', registrado_por=user
    )
    crear_tarifa()

    call_command('generar_cobros', periodo='2025-01')

    cobro = Cobro.objects.get(socio_id=socio.pk, periodo='2025-01')
    assert cobro.cargo_fijo == 6000
    assert cobro.costo_m3_consumido == 20000
    assert cobro.corte_reposicion is None
    assert cobro.total == 26000
    assert cobro.numero_boleta == '2025-00001'
    assert cobro.fecha_vencimiento == date(2025, 2, 28)


@pytest.mark.django_db
def test_generar_cobros_es_idempotente():
    user = User.objects.create_user(username='operario', password='test1234')
    ruta = Ruta.objects.create(codigo='G02')
    socio = crear_socio(2, '22222222-2', ruta)
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-G02', estado_servicio='activo')
    Lectura.objects.create(
        medidor=medidor, periodo='2025-01', lectura_actual=10,
        m3_consumidos=10, origen='operario', registrado_por=user
    )
    crear_tarifa()

    call_command('generar_cobros', periodo='2025-01')
    call_command('generar_cobros', periodo='2025-01')

    assert Cobro.objects.filter(socio_id=socio.pk, periodo='2025-01').count() == 1


@pytest.mark.django_db
def test_generar_cobros_numero_boleta_correlativo():
    user = User.objects.create_user(username='operario', password='test1234')
    ruta = Ruta.objects.create(codigo='G03')
    crear_tarifa()

    for i in range(2):
        socio = crear_socio(10 + i, f'3333333{i}-{i}', ruta)
        medidor = Medidor.objects.create(socio_id=socio, numero_medidor=f'MED-G03-{i}', estado_servicio='activo')
        Lectura.objects.create(
            medidor=medidor, periodo='2025-02', lectura_actual=5,
            m3_consumidos=5, origen='operario', registrado_por=user
        )

    call_command('generar_cobros', periodo='2025-02')

    numeros = sorted(Cobro.objects.filter(periodo='2025-02').values_list('numero_boleta', flat=True))
    assert numeros == ['2025-00001', '2025-00002']


@pytest.mark.django_db
def test_generar_cobros_omite_socio_sin_lectura():
    ruta = Ruta.objects.create(codigo='G04')
    socio = crear_socio(4, '44444444-4', ruta)
    Medidor.objects.create(socio_id=socio, numero_medidor='MED-G04', estado_servicio='activo')
    crear_tarifa()

    call_command('generar_cobros', periodo='2025-01')

    assert not Cobro.objects.filter(socio_id=socio.pk).exists()


@pytest.mark.django_db
def test_generar_cobros_agrega_cargo_reposicion_y_no_lo_duplica():
    user = User.objects.create_user(username='operario', password='test1234')
    ruta = Ruta.objects.create(codigo='G05')
    socio = crear_socio(5, '55555555-5', ruta)
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-G05', estado_servicio='activo')
    tarifa = crear_tarifa()

    lectura_previa = Lectura.objects.create(
        medidor=medidor, periodo='2024-12', lectura_actual=0,
        m3_consumidos=0, origen='operario', registrado_por=user
    )
    cobro_previo = Cobro.objects.create(
        socio=socio, lectura=lectura_previa, tarifa=tarifa, periodo='2024-12',
        cargo_fijo=6000, costo_m3_consumido=0, total=6000,
        fecha_vencimiento=date(2025, 1, 31)
    )
    corte = Cortes.objects.create(
        socio=socio, cobro=cobro_previo, fecha_corte=date(2025, 1, 5),
        lectura_corte=0, operador_corte=user, estado='repuesto',
        fecha_reposicion=date(2025, 1, 10), lectura_reposicion=0,
    )
    Lectura.objects.create(
        medidor=medidor, periodo='2025-01', lectura_actual=10,
        m3_consumidos=10, origen='operario', registrado_por=user
    )

    call_command('generar_cobros', periodo='2025-01')

    cobro = Cobro.objects.get(socio_id=socio.pk, periodo='2025-01')
    assert cobro.corte_reposicion == 50000
    assert cobro.total == 6000 + 10000 + 50000
    corte.refresh_from_db()
    assert corte.costo_reposicion_facturado is True

    # Un segundo período no debe volver a cobrar la reposición
    Lectura.objects.create(
        medidor=medidor, periodo='2025-02', lectura_actual=15,
        m3_consumidos=5, origen='operario', registrado_por=user
    )
    call_command('generar_cobros', periodo='2025-02')
    cobro_siguiente = Cobro.objects.get(socio_id=socio.pk, periodo='2025-02')
    assert cobro_siguiente.corte_reposicion is None


@pytest.mark.django_db
def test_generar_cobros_genera_corte_por_tres_meses_impagos():
    user = User.objects.create_user(username='operario', password='test1234')
    ruta = Ruta.objects.create(codigo='G06')
    socio = crear_socio(6, '66666666-6', ruta)
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-G06', estado_servicio='activo')
    tarifa = crear_tarifa()

    lectura_nov = Lectura.objects.create(
        medidor=medidor, periodo='2024-11', lectura_actual=0,
        m3_consumidos=0, origen='operario', registrado_por=user
    )
    Cobro.objects.create(
        socio=socio, lectura=lectura_nov, tarifa=tarifa, periodo='2024-11',
        cargo_fijo=6000, costo_m3_consumido=0, total=6000,
        fecha_vencimiento=date(2025, 1, 1)
    )
    lectura_dic = Lectura.objects.create(
        medidor=medidor, periodo='2024-12', lectura_actual=2,
        m3_consumidos=2, origen='operario', registrado_por=user
    )
    Cobro.objects.create(
        socio=socio, lectura=lectura_dic, tarifa=tarifa, periodo='2024-12',
        cargo_fijo=6000, costo_m3_consumido=2000, total=8000,
        fecha_vencimiento=date(2025, 1, 1)
    )
    Lectura.objects.create(
        medidor=medidor, periodo='2025-01', lectura_actual=2,
        m3_consumidos=0, origen='operario', registrado_por=user
    )

    call_command('generar_cobros', periodo='2025-01')

    # Suma: 6000 (nov) + 8000 (dic) + 6000 (ene, generado por el comando) = 20000 > 18000
    assert Cortes.objects.filter(socio_id=socio.pk, estado='cortado').exists()


@pytest.mark.django_db
def test_generar_cobros_no_corta_si_hubo_abono():
    user = User.objects.create_user(username='operario', password='test1234')
    ruta = Ruta.objects.create(codigo='G07')
    socio = crear_socio(7, '77777777-7', ruta)
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-G07', estado_servicio='activo')
    tarifa = crear_tarifa()

    for periodo in ['2024-11', '2024-12']:
        lectura = Lectura.objects.create(
            medidor=medidor, periodo=periodo, lectura_actual=0,
            m3_consumidos=0, origen='operario', registrado_por=user
        )
        cobro = Cobro.objects.create(
            socio=socio, lectura=lectura, tarifa=tarifa, periodo=periodo,
            cargo_fijo=6000, costo_m3_consumido=0, total=6000,
            fecha_vencimiento=date(2025, 1, 1)
        )
    Pago.objects.create(cobro=cobro, monto_pagado=1000, forma_pago='efectivo', fecha_pago=date(2024, 12, 15))
    Lectura.objects.create(
        medidor=medidor, periodo='2025-01', lectura_actual=0,
        m3_consumidos=0, origen='operario', registrado_por=user
    )

    call_command('generar_cobros', periodo='2025-01')

    assert not Cortes.objects.filter(socio_id=socio.pk).exists()


@pytest.mark.django_db
def test_generar_cobros_no_corta_si_saldo_bajo_umbral():
    user = User.objects.create_user(username='operario', password='test1234')
    ruta = Ruta.objects.create(codigo='G08')
    socio = crear_socio(8, '88888888-8', ruta)
    medidor = Medidor.objects.create(socio_id=socio, numero_medidor='MED-G08', estado_servicio='activo')
    tarifa = Tarifa.objects.create(
        cargo_fijo=5000, precio_m3=1000, costo_corte_reposicion=50000,
        vigente_desde=date(2025, 1, 1), activo=True
    )

    for periodo in ['2024-11', '2024-12']:
        lectura = Lectura.objects.create(
            medidor=medidor, periodo=periodo, lectura_actual=0,
            m3_consumidos=0, origen='operario', registrado_por=user
        )
        Cobro.objects.create(
            socio=socio, lectura=lectura, tarifa=tarifa, periodo=periodo,
            cargo_fijo=5000, costo_m3_consumido=0, total=5000,
            fecha_vencimiento=date(2025, 1, 1)
        )
    Lectura.objects.create(
        medidor=medidor, periodo='2025-01', lectura_actual=0,
        m3_consumidos=0, origen='operario', registrado_por=user
    )

    call_command('generar_cobros', periodo='2025-01')

    # 5000 x 3 = 15000, por debajo del umbral de 18000: no debe cortar
    assert not Cortes.objects.filter(socio_id=socio.pk).exists()


@pytest.mark.django_db
def test_generar_cobros_numero_boleta_reinicia_en_anno_nuevo():
    user = User.objects.create_user(username='operario', password='test1234')
    ruta = Ruta.objects.create(codigo='G09')
    crear_tarifa()

    socio_dic = crear_socio(9, '90909090-3', ruta)
    medidor_dic = Medidor.objects.create(socio_id=socio_dic, numero_medidor='MED-G09-D', estado_servicio='activo')
    Lectura.objects.create(
        medidor=medidor_dic, periodo='2024-12', lectura_actual=5,
        m3_consumidos=5, origen='operario', registrado_por=user
    )

    call_command('generar_cobros', periodo='2024-12')

    cobro_dic = Cobro.objects.get(socio_id=socio_dic.pk, periodo='2024-12')
    assert cobro_dic.numero_boleta == '2024-00001'

    socio_ene = crear_socio(19, '19191919-3', ruta)
    medidor_ene = Medidor.objects.create(socio_id=socio_ene, numero_medidor='MED-G09-E', estado_servicio='activo')
    Lectura.objects.create(
        medidor=medidor_ene, periodo='2025-01', lectura_actual=3,
        m3_consumidos=3, origen='operario', registrado_por=user
    )

    call_command('generar_cobros', periodo='2025-01')

    cobro_ene = Cobro.objects.get(socio_id=socio_ene.pk, periodo='2025-01')
    assert cobro_ene.numero_boleta == '2025-00001'


@pytest.mark.django_db
def test_generar_cobros_alerta_por_correo_si_falla():
    # Si el comando falla a mitad de camino, se debe avisar por correo al
    # administrador y la excepción debe seguir propagándose para que el cron
    # (Oracle Cloud) reporte el fallo por su propio exit code.
    with patch(
        'boletas.management.commands.generar_cobros.Command._generar',
        side_effect=RuntimeError('fallo simulado'),
    ):
        with pytest.raises(RuntimeError):
            call_command('generar_cobros', periodo='2025-01')

    assert len(mail.outbox) == 1
    enviado = mail.outbox[0]
    assert enviado.to == [settings.ADMIN_ALERT_EMAIL]
    assert '2025-01' in enviado.subject
    assert 'fallo simulado' in enviado.body
