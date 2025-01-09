from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Modelo personalizado de usuario basado en AbstractUser.
    
    Permite agregar campos adicionales en el futuro si es necesario.
    """
    email = models.EmailField(unique=True)

    def __str__(self):
        """
        Devuelve una representación legible del usuario.
        """
        return self.username
