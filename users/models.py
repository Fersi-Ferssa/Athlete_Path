from django.db import models
from django.contrib.auth.models import User
from .countries import COUNTRY_CHOICES  # La lista de países ya existente

class Profile(models.Model):
    ROLE_CHOICES = [
        ('Athlete', 'Atleta'),
        ('Coach', 'Coach'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    olympic_country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    discipline = models.CharField(max_length=100, choices=[('Gymnastics', 'Gimnasia Artística')])
    branch = models.CharField(max_length=100, choices=[
        ('Uneven Bars', 'Barras Asimétricas'),
        ('Balance Beam', 'Barra de Equilibrio'),
        ('Floor', 'Piso')
    ])
    team_name = models.CharField(max_length=100, blank=True, null=True)  # Editable solo por coaches
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='Athlete')
    security_answer = models.CharField(max_length=255, blank=False, default='No contestada')

    def __str__(self):
        return f'{self.user.username} - {self.discipline} ({self.branch})'

    def is_coach(self):
        return self.role == 'Coach'

    def is_athlete(self):
        return self.role == 'Athlete'

# Modelo para los récords confidenciales de los atletas
class AthleteRecord(models.Model):
    athlete = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'Athlete'}, related_name='athlete_records')
    coach = models.ForeignKey(Profile, on_delete=models.CASCADE, limit_choices_to={'role': 'Coach'}, related_name='coach_records')
    difficulty = models.IntegerField(choices=[(i, i) for i in range(1, 8)])  # Dificultad del 1 al 7
    execution = models.IntegerField(choices=[(i, i) for i in range(1, 11)])  # Ejecución del 1 al 10
    notes = models.TextField(max_length=250, blank=True, null=True)  # Notas del entrenador (opcional)
    created_at = models.DateTimeField(auto_now_add=True)
    evaluation_date = models.DateField(null=True, blank=True)  # Nuevo campo para la fecha de evaluación

    def __str__(self):
        return f"Record for {self.athlete.user.username} by {self.coach.user.username}"
    
    def total_score(self):
        return self.difficulty + self.execution  # Suma de dificultad y ejecución