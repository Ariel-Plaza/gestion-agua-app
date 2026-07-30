from django.urls import path
from .views import AgregarTarifa, ListaTarifas, MostrarTarifaPorAnno, ActualizarTarifa, EliminarTarifa, GenerarCobro, ListaCobrosPorSocio, DetalleCobro, CuponCobro, RegistrarPago, ListaPagosPorCobro

urlpatterns = [
    # Tarifa
    path('tarifas/', ListaTarifas.as_view(), name='lista-tarifas'),
    path('tarifas/agregar/', AgregarTarifa.as_view(), name='agregar-tarifa'),
    path('tarifas/<int:fecha>/', MostrarTarifaPorAnno.as_view(), name='buscar-tarifa'),
    path('tarifas/actualizar/<int:pk>/', ActualizarTarifa.as_view(), name='actualizar-tarifa'),
    path('tarifas/eliminar/<int:pk>/', EliminarTarifa.as_view(), name='eliminar-tarifa'),

    # Cobro
    path('cobros/', GenerarCobro.as_view(), name='generar-cobro'),
    path('cobros/socio/<str:rut>/', ListaCobrosPorSocio.as_view(), name='lista-cobros-socio'),
    path('cobros/<int:pk>/', DetalleCobro.as_view(), name='detalle-cobro'),
    path('cobros/<int:pk>/cupon/', CuponCobro.as_view(), name='cupon-cobro'),

    # Pago
    path('pagos/', RegistrarPago.as_view(), name='registrar-pago'),
    path('pagos/cobro/<int:cobro_id>/', ListaPagosPorCobro.as_view(), name='lista-pagos-cobro'),
]