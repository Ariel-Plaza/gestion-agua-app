from django.urls import path
from .views import ReporteDeudores

urlpatterns = [
    path('deudores/', ReporteDeudores.as_view(), name='reporte-deudores'),
]
