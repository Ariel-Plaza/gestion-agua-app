from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from usuarios.permissions import EsPersonalDelComite
from boletas.models import Cobro
from cortes.models import Cortes


def formato_clp(valor):
    # Separador de miles con punto, como se usa en Chile ($16.000)
    return f"{int(valor):,}".replace(',', '.')


def calcular_deudores():
    # Un socio entra al listado si tiene algún Cobro vencido y/o un Corte activo
    cobros_por_socio = {}
    for cobro in Cobro.objects.all():
        cobros_por_socio.setdefault(cobro.socio_id, []).append(cobro)

    cortes_activos = set(
        corte.socio_id for corte in Cortes.objects.filter(estado='cortado')
    )

    filas = []
    total_adeudado = 0
    for socio_id, cobros in cobros_por_socio.items():
        vencidos = [c for c in cobros if c.estado == 'vencido']
        corte_activo = socio_id in cortes_activos
        if not vencidos and not corte_activo:
            continue

        saldo = sum(c.saldo_pendiente for c in cobros if c.saldo_pendiente > 0)
        total_adeudado += saldo
        filas.append({
            'socio': cobros[0].socio,
            'saldo': saldo,
            'saldo_fmt': formato_clp(saldo),
            'meses_atraso': len(vencidos),
            'corte_activo': corte_activo,
        })

    filas.sort(key=lambda f: f['socio'].rut)
    return filas, total_adeudado


class ReporteDeudores(APIView):
    permission_classes = [EsPersonalDelComite]

    def get(self, request):
        filas, total_adeudado = calcular_deudores()

        contexto = {
            'filas': filas,
            'total_adeudado_fmt': formato_clp(total_adeudado),
            'fecha_generacion': timezone.localdate(),
        }
        html = render_to_string('reportes/deudores.html', contexto)
        pdf = HTML(string=html).write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte-deudores.pdf"'
        return response


class ReporteRecaudacion(APIView):
    permission_classes = [EsPersonalDelComite]

    def get(self, request):
        periodo = request.query_params.get('periodo')
        if not periodo:
            return Response(
                {'error': 'Debes indicar el período a consultar (?periodo=YYYY-MM)'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cobros = Cobro.objects.filter(periodo=periodo)
        total_facturado = sum(c.total for c in cobros)
        total_cobrado = sum(c.total_pagado for c in cobros)
        total_pendiente = total_facturado - total_cobrado
        porcentaje_cobrado = round(total_cobrado / total_facturado * 100, 1) if total_facturado else 0

        contexto = {
            'periodo': periodo,
            'cantidad_cobros': cobros.count(),
            'total_facturado_fmt': formato_clp(total_facturado),
            'total_cobrado_fmt': formato_clp(total_cobrado),
            'total_pendiente_fmt': formato_clp(total_pendiente),
            'porcentaje_cobrado': porcentaje_cobrado,
        }
        html = render_to_string('reportes/recaudacion.html', contexto)
        pdf = HTML(string=html).write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="recaudacion-{periodo}.pdf"'
        return response
