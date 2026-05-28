from django.db import models

class Ruta(models.Model):
    codigo = models.CharField(max_length=100, null=False, unique=True)