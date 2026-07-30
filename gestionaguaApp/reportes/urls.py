from django.urls import path
from .views import ReporteDeudores, ReporteRecaudacion

urlpatterns = [
    path('deudores/', ReporteDeudores.as_view(), name='reporte-deudores'),
    path('recaudacion/', ReporteRecaudacion.as_view(), name='reporte-recaudacion'),
]
