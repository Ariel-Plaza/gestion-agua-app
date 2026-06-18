from django.db import models

class Tarifa(models.Model):
    cargo_fijo = models.IntegerField(null=False)
    precio_m3 = models.IntegerField(null=False)
    vigente_desde = models.DateField(null=False)
    vigente_hasta = models.DateField(null=True)
    costo_corte_reposicion = models.IntegerField(null=False)
    activo = models.BooleanField(null=False, default=True)