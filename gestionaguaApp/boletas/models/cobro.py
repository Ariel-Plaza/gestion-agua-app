from django.db import models
from socios.models import Socio
from lecturas.models import Lectura
from .models.tarifa import Tarifa

class Cobro(models.Model):
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('vencido', 'Vencido'),
    ]
    
    socio = models.ForeignKey(Socio, on_delete=models.PROTECT)
    lectura = models.ForeignKey(Lectura, on_delete=models.PROTECT)
    tarifa = models.ForeignKey(Tarifa, on_delete=models.PROTECT)
    periodo = models.CharField(max_length=7)  # formato YYYY-MM
    cargo_fijo = models.IntegerField()
    costo_m3_consumido = models.IntegerField()
    corte_reposicion = models.IntegerField(null=True, blank=True)
    saldo_pendiente = models.IntegerField(null=True, blank=True)
    abono = models.IntegerField(null=True, blank=True)
    interes_mora = models.IntegerField(null=True, blank=True)
    total = models.IntegerField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    numero_boleta = models.CharField(max_length=20, null=True, blank=True)
    fecha_emision = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField()

    def __str__(self):
        return f"Cobro {self.numero_boleta} - {self.socio} - {self.periodo}"