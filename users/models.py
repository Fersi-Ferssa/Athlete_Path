from django.db import models
from django.contrib.auth.models import User
from .countries import COUNTRY_CHOICES  # La lista de países ya existente

# Modelo de perfil que extiende al usuario de Django
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    olympic_country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    discipline = models.CharField(max_length=100, choices=[('Gymnastics', 'Gimnasia Artística')])
    branch = models.CharField(max_length=100, choices=[
        ('Uneven Bars', 'Barras Asimétricas'),
        ('Balance Beam', 'Barra de Equilibrio'),
        ('Floor', 'Piso')
    ])
    team_name = models.CharField(max_length=100, blank=True, null=True)  # Solo para coaches
    role = models.CharField(max_length=50, choices=[('Athlete', 'Atleta'), ('Coach', 'Entrenador')])  # El rol debe ser guardado

    def __str__(self):
        return f'{self.user.username} - {self.role}'

    # Métodos para verificar si el perfil es de un atleta o coach
    def is_athlete(self):
        return self.role == 'Athlete'

    def is_coach(self):
        return self.role == 'Coach'

# Modelo para los récords confidenciales de los atletas
class AthleteRecord(models.Model):
    athlete = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'Athlete'}, related_name='athlete_records')
    coach = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'Coach'}, related_name='coach_records')
    difficulty = models.IntegerField(choices=[(i, i) for i in range(1, 8)])  # Dificultad del 1 al 7
    execution = models.IntegerField(choices=[(i, i) for i in range(1, 11)])  # Ejecución del 1 al 10
    notes = models.TextField(max_length=250, blank=True, null=True)  # Notas del entrenador (opcional)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Record for {self.athlete.user.username} by {self.coach.user.username}"
