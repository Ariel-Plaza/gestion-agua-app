from django.db import models
from django.contrib.auth.models import AbstractUser

# username, password, email, first_name, last_name
# extiendo de AbstractUser
class Usuario(AbstractUser):
    # defino roles
    ROL_CHOICES = [
        ('administrador', 'Administrador'),
        ('operador','Operador'),
        ('funcionario','Funcionario'),
        ('socio','Socio')
    ]
    #defino campo rol y asigno ROL_CHOICES
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='socio'
    )