from django.db import models
from socios.models import Socio
from boletas.models import Cobro
from usuarios.models import Usuario


class Cortes(models.Model):

    ESTADO_CHOICES = [
        ('cortado', 'Cortado'),
        ('repuesto', 'Repuesto'),
    ]

    socio = models.ForeignKey(Socio, on_delete=models.PROTECT, related_name='cortes')
    cobro = models.ForeignKey(Cobro, on_delete=models.PROTECT, related_name='cortes')

    fecha_corte = models.DateField()
    lectura_corte = models.IntegerField()
    operador_corte = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='cortes_realizados')

    fecha_reposicion = models.DateField(null=True, blank=True)
    lectura_reposicion = models.IntegerField(null=True, blank=True)

    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='cortado')

    # Se marca True cuando el cargo de reposición ($50.000) ya fue agregado
    # a un Cobro por el cron de generar_cobros. Evita cobrarlo más de una vez.
    costo_reposicion_facturado = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha_corte']

    def __str__(self):
        return f"Corte {self.socio} — {self.fecha_corte} — {self.estado}"