from django.urls import path
from .views import AgregarLectura, ListaLecturas, ObtenerLecturaPorId, ActualizarLectura

urlpatterns = [
    path('', ListaLecturas.as_view(), name='lista-lecturas'),
    path('agregar/', AgregarLectura.as_view(), name='agregar-lectura'),
    path('buscar/<int:pk>/', ObtenerLecturaPorId.as_view(), name='buscar-lectura'),
    path('actualizar/<int:pk>/', ActualizarLectura.as_view(), name='actualizar-lectura'),
]