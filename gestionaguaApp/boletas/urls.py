from django.urls import path
from .views import AgregarTarifa, ListaTarifas, MostrarTarifaPorAnno, ActualizarTarifa, EliminarTarifa, GenerarCobro, ListaCobrosPorSocio, DetalleCobro, RegistrarPago, ListaPagosPorCobro

urlpatterns = [
    path('agregar/', AgregarTarifa.as_view(), name='agregar-tarifa'),
    path('', ListaTarifas.as_view(), name='lista-tarifas'),
    path('buscar/<int:fecha>/', MostrarTarifaPorAnno.as_view(), name='buscar-tarifa'),
    
    path('actualizar/<int:pk>/', ActualizarTarifa.as_view(), name='actualizar-tarifa'),
    path('eliminar/<int:pk>/', EliminarTarifa.as_view(), name='eliminar-tarifa'),
    path('cobros/agregar/', GenerarCobro.as_view(), name='generar-cobro'),
    path('cobros/<str:rut>/', ListaCobrosPorSocio.as_view(), name='lista-cobros-socio'),
    path('cobros/detalle/<int:pk>/', DetalleCobro.as_view(), name='detalle-cobro'),
    path('pagos/agregar/', RegistrarPago.as_view(), name='registrar-pago'),
path('pagos/<int:cobro_id>/', ListaPagosPorCobro.as_view(), name='lista-pagos-cobro'),
]