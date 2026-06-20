from django.db import models
from django.utils import timezone
from socios.models import Socio
from lecturas.models import Lectura
from .tarifa import Tarifa


class Cobro(models.Model):

    socio = models.ForeignKey(Socio, on_delete=models.PROTECT, related_name='cobros')
    lectura = models.ForeignKey(Lectura, on_delete=models.PROTECT, related_name='cobros')
    tarifa = models.ForeignKey(Tarifa, on_delete=models.PROTECT, related_name='cobros')

    periodo = models.CharField(max_length=7)  # formato: "YYYY-MM"

    cargo_fijo = models.IntegerField()
    costo_m3_consumido = models.IntegerField()
    corte_reposicion = models.IntegerField(null=True, blank=True)
    interes_mora = models.IntegerField(null=True, blank=True)

    total = models.IntegerField()
    numero_boleta = models.CharField(max_length=20, unique=True, null=True, blank=True)
    fecha_emision = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['socio', 'periodo'], name='unique_cobro_socio_periodo')
        ]
        ordering = ['-periodo']

    def __str__(self):
        return f"Cobro {self.numero_boleta} - {self.socio} - {self.periodo}"

    @property
    def total_pagado(self):
        return self.pagos.aggregate(
            total=models.Sum('monto_pagado')
        )['total'] or 0

    @property
    def saldo_pendiente(self):
        return self.total - self.total_pagado

    @property
    def estado(self):
        if self.saldo_pendiente == 0:
            return 'pagado'
        elif self.fecha_vencimiento < timezone.now().date():
            return 'vencido'
        return 'pendiente'