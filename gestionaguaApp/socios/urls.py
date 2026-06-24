from django.urls import path
from .views import (
    AgregarSocio, ListaSocios, ObtenerSocioNombreApellidos, ActualizarSocio, EliminarSocio,
    ListaRutas, AgregarRuta, ActualizarRuta, EliminarRuta,
    ListaMedidores, AgregarMedidor, ObtenerMedidorPorSocio, ActualizarMedidor, EliminarMedidor,
)

urlpatterns = [
    # Socios
    path('', ListaSocios.as_view(), name='lista-socios'),
    path('buscar/', ObtenerSocioNombreApellidos.as_view(), name='buscar-socio'),
    path('agregar/', AgregarSocio.as_view(), name='agregar-socio'),
    path('actualizar/<int:pk>/', ActualizarSocio.as_view(), name='actualizar-socio'),
    path('eliminar/<int:pk>/', EliminarSocio.as_view(), name='eliminar-socio'),

    # Rutas
    path('rutas/', ListaRutas.as_view(), name='lista-rutas'),
    path('rutas/agregar/', AgregarRuta.as_view(), name='agregar-ruta'),
    path('rutas/actualizar/<int:pk>/', ActualizarRuta.as_view(), name='actualizar-ruta'),
    path('rutas/eliminar/<int:pk>/', EliminarRuta.as_view(), name='eliminar-ruta'),

    # Medidores
    path('medidores/', ListaMedidores.as_view(), name='lista-medidores'),
    path('medidores/agregar/', AgregarMedidor.as_view(), name='agregar-medidor'),
    path('medidores/socio/<int:socio_id>/', ObtenerMedidorPorSocio.as_view(), name='medidor-por-socio'),
    path('medidores/actualizar/<int:pk>/', ActualizarMedidor.as_view(), name='actualizar-medidor'),
    path('medidores/eliminar/<int:pk>/', EliminarMedidor.as_view(), name='eliminar-medidor'),
]