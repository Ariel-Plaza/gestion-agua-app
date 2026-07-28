import calendar
from datetime import date

from django.core.management.base import BaseCommand
from django.db import IntegrityError

from socios.models import Socio, Medidor
from lecturas.models import Lectura
from usuarios.models import Usuario
from boletas.models import Tarifa, Cobro
from cortes.models import Cortes

UMBRAL_CORTE = 18000
MESES_CONSECUTIVOS_CORTE = 3


def periodo_actual():
    hoy = date.today()
    return f"{hoy.year:04d}-{hoy.month:02d}"


def periodo_siguiente(periodo):
    anio, mes = (int(p) for p in periodo.split('-'))
    mes += 1
    if mes > 12:
        mes = 1
        anio += 1
    return f"{anio:04d}-{mes:02d}"


def periodo_anterior(periodo):
    anio, mes = (int(p) for p in periodo.split('-'))
    mes -= 1
    if mes < 1:
        mes = 12
        anio -= 1
    return f"{anio:04d}-{mes:02d}"


def fecha_vencimiento_para(periodo):
    # Vence el último día del mes siguiente al periodo facturado
    siguiente = periodo_siguiente(periodo)
    anio, mes = (int(p) for p in siguiente.split('-'))
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    return date(anio, mes, ultimo_dia)


class Command(BaseCommand):
    help = 'Genera los cobros mensuales del período y evalúa cortes de servicio.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--periodo', type=str, default=None,
            help='Período a facturar en formato YYYY-MM (por defecto: mes actual).'
        )

    def handle(self, *args, **options):
        periodo = options['periodo'] or periodo_actual()
        self.stdout.write(f'Generando cobros para el período {periodo}...')

        operador_sistema = self.obtener_operador_sistema()

        cobros_generados = 0
        cobros_omitidos = 0

        siguiente_numero_por_anio = {}

        for socio in Socio.objects.filter(activo=True):
            medidores_activos = Medidor.objects.filter(socio_id=socio.pk, estado_servicio='activo')
            medidor = medidores_activos.first()
            if medidor is None:
                cobros_omitidos += 1
                continue

            if Cobro.objects.filter(socio_id=socio.pk, periodo=periodo).exists():
                cobros_omitidos += 1
                continue

            lecturas_periodo = Lectura.objects.filter(medidor_id=medidor.pk, periodo=periodo)
            lectura = lecturas_periodo.first()
            if lectura is None:
                self.stdout.write(
                    f'  Sin lectura de {periodo} para socio {socio.rut} (medidor {medidor.numero_medidor}), se omite.'
                )
                cobros_omitidos += 1
                continue

            tarifa = Tarifa.objects.filter(activo=True).order_by('-vigente_desde').first()
            if tarifa is None:
                self.stdout.write('  No hay tarifa activa configurada, se detiene la generación.')
                break

            anio_periodo = periodo.split('-')[0]
            if anio_periodo not in siguiente_numero_por_anio:
                siguiente_numero_por_anio[anio_periodo] = self.siguiente_numero_boleta(anio_periodo)

            numero_boleta = f"{anio_periodo}-{siguiente_numero_por_anio[anio_periodo]:05d}"
            siguiente_numero_por_anio[anio_periodo] += 1

            cargo_fijo = tarifa.cargo_fijo
            costo_m3_consumido = round(lectura.m3_consumidos * tarifa.precio_m3)

            corte_reposicion = None
            corte_pendiente = Cortes.objects.filter(
                socio_id=socio.pk, estado='repuesto', costo_reposicion_facturado=False
            ).first()
            if corte_pendiente:
                corte_reposicion = tarifa.costo_corte_reposicion

            total = cargo_fijo + costo_m3_consumido + (corte_reposicion or 0)

            try:
                Cobro.objects.create(
                    socio=socio,
                    lectura=lectura,
                    tarifa=tarifa,
                    periodo=periodo,
                    cargo_fijo=cargo_fijo,
                    costo_m3_consumido=costo_m3_consumido,
                    corte_reposicion=corte_reposicion,
                    total=total,
                    numero_boleta=numero_boleta,
                    fecha_vencimiento=fecha_vencimiento_para(periodo),
                )
            except IntegrityError:
                cobros_omitidos += 1
                continue

            if corte_pendiente:
                corte_pendiente.costo_reposicion_facturado = True
                corte_pendiente.save()

            cobros_generados += 1

        self.stdout.write(f'Cobros generados: {cobros_generados}. Omitidos: {cobros_omitidos}.')

        cortes_generados = self.evaluar_cortes(operador_sistema)
        self.stdout.write(f'Cortes generados: {cortes_generados}.')

    def obtener_operador_sistema(self):
        operador, creado = Usuario.objects.get_or_create(
            username='sistema', defaults={'rol': 'administrador'}
        )
        if creado:
            operador.set_unusable_password()
            operador.save()
        return operador

    def siguiente_numero_boleta(self, anio):
        cobros_con_numero = Cobro.objects.exclude(numero_boleta=None)
        prefijo = f"{anio}-"
        numeros = [
            int(c.numero_boleta.split('-')[-1])
            for c in cobros_con_numero
            if c.numero_boleta.startswith(prefijo)
        ]
        return (max(numeros) + 1) if numeros else 1

    def evaluar_cortes(self, operador_sistema):
        cortes_generados = 0

        for socio in Socio.objects.filter(activo=True):
            if Cortes.objects.filter(socio_id=socio.pk, estado='cortado').exists():
                continue

            ultimos_cobros = list(Cobro.objects.filter(socio_id=socio.pk)[:MESES_CONSECUTIVOS_CORTE])
            if len(ultimos_cobros) < MESES_CONSECUTIVOS_CORTE:
                continue

            # Cobro.Meta.ordering = ['-periodo'], por lo que vienen del más reciente al más antiguo
            son_consecutivos = all(
                ultimos_cobros[i + 1].periodo == periodo_anterior(ultimos_cobros[i].periodo)
                for i in range(len(ultimos_cobros) - 1)
            )
            if not son_consecutivos:
                continue

            sin_ningun_abono = all(c.total_pagado == 0 for c in ultimos_cobros)
            if not sin_ningun_abono:
                continue

            saldo_periodo = sum(c.total for c in ultimos_cobros)
            if saldo_periodo <= UMBRAL_CORTE:
                continue

            cobro_mas_reciente = ultimos_cobros[0]
            Cortes.objects.create(
                socio=socio,
                cobro=cobro_mas_reciente,
                fecha_corte=date.today(),
                lectura_corte=round(cobro_mas_reciente.lectura.lectura_actual),
                operador_corte=operador_sistema,
                estado='cortado',
            )
            cortes_generados += 1

        return cortes_generados
