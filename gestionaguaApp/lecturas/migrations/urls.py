from django.urls import path
from .views import AgregarSocio, ListaSocios, ObtenerSocioNombreApellidos, ActualizarSocio, EliminarSocio

urlpatterns = [
    path('', ListaSocios.as_view(), name='lista-socios'),
    path('buscar/', ObtenerSocioNombreApellidos.as_view(), name='buscar-socio'),
    path('agregar/', AgregarSocio.as_view(), name='agregar-socio'),
    path('actualizar/<int:pk>/', ActualizarSocio.as_view(), name='actualizar-socio'),
    path('eliminar/<int:pk>/', EliminarSocio.as_view(), name='eliminar-socio'),
    
]