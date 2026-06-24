from django.db import models
from .ruta import Ruta

class Socio(models.Model):
    numero_socio = models.IntegerField(unique=True)
    # agregar validar de rut segun el -k
    rut = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=30, null=False)
    apellido = models.CharField(max_length=30,null=False)
    segundo_apellido = models.CharField(max_length=30, null=True, blank=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    ruta_id = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    referencia_direccion = models.CharField(max_length=500)
    subsidio = models.BooleanField(null=False, default=False)
    activo = models.BooleanField(null=False, default=True)
    fecha_registro = models.DateField(null=False, auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} - N°{self.numero_socio}"