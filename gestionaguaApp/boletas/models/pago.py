from django.db import models
from .cobro import Cobro
class Pago(models.Model):
    FORMA_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
    ]
    
    cobro = models.ForeignKey(Cobro, on_delete=models.PROTECT, related_name='pagos')
    monto_pagado = models.IntegerField()
    forma_pago = models.CharField(max_length=15, choices=FORMA_PAGO_CHOICES)
    fecha_pago = models.DateField(auto_now_add=True)