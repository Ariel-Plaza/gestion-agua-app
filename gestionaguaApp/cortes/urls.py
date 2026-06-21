from django.urls import path
from .views import RegistrarCorte, RegistrarReposicion, ListaCortesPorSocio, DetalleCorte

urlpatterns = [
    path('', RegistrarCorte.as_view(), name='registrar-corte'),
    path('<int:pk>/reposicion/', RegistrarReposicion.as_view(), name='registrar-reposicion'),
    path('socio/<str:rut>/', ListaCortesPorSocio.as_view(), name='lista-cortes-socio'),
    path('<int:pk>/', DetalleCorte.as_view(), name='detalle-corte'),
]