from django.db import models  # Importa el módulo de modelos de Django
from django.contrib.auth.models import User  # Importa el modelo de usuario predeterminado de Django
from .countries import COUNTRY_CHOICES  # Importa la lista de opciones de países desde el archivo countries.py

# Define un modelo llamado Profile, que extiende la información del usuario.
class Profile(models.Model):
    # Relación uno a uno con el modelo User de Django, lo que significa que cada usuario tendrá un único perfil asociado.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Campo para almacenar el primer apellido del usuario, limitado a un máximo de 150 caracteres.
    first_last_name = models.CharField(max_length=150)
    # Campo para almacenar la fecha de nacimiento del usuario.
    date_of_birth = models.DateField()
    # Campo para almacenar el país, utilizando un código de país de 2 caracteres y las opciones definidas en COUNTRY_CHOICES.
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    # Campo para almacenar el sexo del usuario, con opciones limitadas a 'Male' o 'Female'.
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    # Campo para definir el rol del usuario, ya sea 'Athlete' o 'Coach'.
    role = models.CharField(max_length=50, choices=[('Athlete', 'Athlete'), ('Coach', 'Coach')])

    # Método para representar el objeto Profile como una cadena, que devolverá el nombre de usuario relacionado con el perfil.
    def __str__(self):
        return f'{self.user.username} Profile'
