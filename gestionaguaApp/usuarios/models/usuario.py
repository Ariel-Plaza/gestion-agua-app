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
    # Vincula un usuario con rol='socio' a su propio registro de Socio.
    # Queda en None para administrador/operador/funcionario, que no representan a un socio.
    socio = models.OneToOneField(
        'socios.Socio', on_delete=models.SET_NULL, null=True, blank=True, related_name='usuario'
    )

    def __str__(self):
        return f"{self.get_full_name()} ({self.rol})"