from django.urls import path
from .views import ListaSocios, ObtenerSocioNombreApellidos

urlpatterns = [
    path('', ListaSocios.as_view(), name='lista-socios'),
    path('buscar/', ObtenerSocioNombreApellidos.as_view(), name='buscar-socio'),
]