from django.urls import path
from .views import AgregarTarifa, ListaTarifas, MostrarTarifaPorAnno, ActualizarTarifa, EliminarTarifa

urlpatterns = [
    path('agregar/', AgregarTarifa.as_view(), name='agregar-tarifa'),
    path('', ListaTarifas.as_view(), name='lista-tarifas'),
    path('buscar/<int:fecha>/', MostrarTarifaPorAnno.as_view(), name='buscar-tarifa'),
    
    path('actualizar/<int:pk>/', ActualizarTarifa.as_view(), name='actualizar-tarifa'),
    path('eliminar/<int:pk>/', EliminarTarifa.as_view(), name='eliminar-tarifa'),
    
]