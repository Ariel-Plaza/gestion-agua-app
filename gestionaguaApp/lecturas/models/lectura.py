from django.db import models
from socios.models import Medidor
from usuarios.models import Usuario


class Lectura(models.Model):

    ORIGEN_CHOICES = [
        ("socio", "Socio"),
        ("operario", "Operario"),
        ("administrador", "Administrador"),
    ]

    medidor = models.ForeignKey(Medidor, on_delete=models.PROTECT)
    periodo = models.CharField(max_length=7)  # formato: YYYY-MM
    lectura_actual = models.DecimalField(max_digits=10, decimal_places=2)
    m3_consumidos = models.DecimalField(max_digits=10, decimal_places=2)
    origen = models.CharField(max_length=13, choices=ORIGEN_CHOICES)
    entregado_por = models.CharField(max_length=100, null=True, blank=True)
    registrado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Lectura {self.periodo} - Medidor {self.medidor_id} ({self.m3_consumidos} m³)"

    class Meta:
        unique_together = ("medidor", "periodo")

    def get_lectura_anterior(self):
        todas = Lectura.objects.filter(medidor=self.medidor).order_by("periodo")
        anteriores = [l for l in todas if l.periodo < self.periodo]
        return anteriores[-1] if anteriores else None

    def get_lecturas_posteriores(self):
        todas = Lectura.objects.filter(medidor=self.medidor).order_by("periodo")
        return [l for l in todas if l.periodo > self.periodo]

    def save(self, *args, **kwargs):
        anterior = self.get_lectura_anterior()

        if anterior:
            self.m3_consumidos = self.lectura_actual - anterior.lectura_actual
            if self.m3_consumidos < 0:
                raise ValueError(
                    "La lectura actual no puede ser menor que la lectura anterior"
                )
        else:
            self.m3_consumidos = 0

        super().save(*args, **kwargs)

        for posterior in self.get_lecturas_posteriores():
            lectura_previa = posterior.get_lectura_anterior()
            nuevo_consumo = posterior.lectura_actual - lectura_previa.lectura_actual
            if nuevo_consumo != posterior.m3_consumidos:
                Lectura.objects.filter(pk=posterior.pk).update(
                    m3_consumidos=nuevo_consumo
                )
