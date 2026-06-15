from django.db import models
from socios.models import Medidor
from usuarios.models import Usuario

class Lectura(models.Model):

    ORIGEN_CHOICES = [
        ('socio', 'Socio'),
        ('operario', 'Operario'),
        ('administrador', 'Administrador'),
    ]

    medidor = models.ForeignKey(Medidor, on_delete=models.PROTECT)
    periodo = models.CharField(max_length=7)  # formato: YYYY-MM
    lectura_actual = models.DecimalField(max_digits=10, decimal_places=2)
    m3_consumidos = models.DecimalField(max_digits=10, decimal_places=2)
    origen = models.CharField(max_length=13, choices=ORIGEN_CHOICES)
    entregado_por = models.CharField(max_length=100, null=True, blank=True)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    fecha_registro = models.DateField(auto_now_add=True)

    class Meta:
        # Un medidor solo puede tener una lectura por periodo
        unique_together = ('medidor', 'periodo')
        
        
    def save(self, *args, **kwargs):
        lectura_anterior = Lectura.objects.filter(
            medidor=self.medidor
            ).exclude(
                periodo=self.periodo
            ).order_by('-periodo').first()
        
        if lectura_anterior :
            self.m3_consumidos = self.lectura_actual - lectura_anterior.lectura_actual
            if self.m3_consumidos < 0:
                raise ValueError("La lectura actual no puede ser menor que la lectura anterior")

        else:
            self.m3_consumidos = 0
        super().save(*args, **kwargs)