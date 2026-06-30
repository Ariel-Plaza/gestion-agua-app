from django.db import models
from .socio import Socio

class Medidor(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('cortado', 'Cortado'),
        ('retirado', 'Retirado'),
    ]
    
    socio_id= models.ForeignKey(Socio, on_delete=models.CASCADE)
    numero_medidor = models.CharField(max_length=10 ,null=False, unique=True )
    estado_servicio = models.CharField(max_length=10 ,null=False, default='activo', choices=ESTADO_CHOICES)
    fecha_instalacion = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Medidor {self.numero_medidor} - {self.socio_id}"