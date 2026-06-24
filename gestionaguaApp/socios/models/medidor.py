from django.db import models
from .socio import Socio

class Medidor(models.Model):
    socio_id= models.ForeignKey(Socio, on_delete=models.CASCADE)
    numero_medidor = models.CharField(max_length=10 ,null=False, unique=True )
    estado_servicio = models.CharField(max_length=10 ,null=False)
    fecha_instalacion = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Medidor {self.numero_medidor} - {self.socio_id}"