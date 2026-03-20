from django.urls import path
from .views import ListaSocios, ObtenerSocioNombreApellidos

urlpatterns = [
    path('', ListaSocios.as_view(), name='lista-socios'),
    path('<int:pk>/', ObtenerSocioNombreApellidos.as_view(), name='detalle-socio'),
]