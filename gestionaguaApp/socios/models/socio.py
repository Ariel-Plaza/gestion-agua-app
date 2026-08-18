from django.db import models
from .ruta import Ruta

from django.utils import timezone

# Clase con sus caracteristicas y una funcion
class Socio(models.Model):
    # valor unico por cada socio
    numero_socio = models.IntegerField(unique=True)
    # agregar validar de rut segun el -k 
    # valor unique para que no se repita, registros unicos en la BD
    rut = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=30, null=False)
    apellido = models.CharField(max_length=30,null=False)
    segundo_apellido = models.CharField(max_length=30, null=True, blank=True)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    # valor unico, puede ser nulo, puede quedar en blanco 
    email = models.EmailField(unique=True, null=True, blank=True)
    # es una relacion con ruta a travez de Foreign key y al borrar se debe borrar los datos relacionados
    ruta_id = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    referencia_direccion = models.CharField(max_length=500)
    subsidio = models.BooleanField(null=False, default=False)
    activo = models.BooleanField(null=False, default=True)
    # registra la fecha del lugar donde se esta utilizando el sistema
    fecha_registro = models.DateField(default=timezone.localdate)
    
    # funcion que es un autollamado a Socio y responde con nombre, apellido, numero de socio, la puedo llenar con mas datos, segun sea necesario
    def __str__(self):
        return f"{self.nombre} {self.apellido} - N°{self.numero_socio}"