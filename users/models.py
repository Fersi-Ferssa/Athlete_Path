from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
# Importa la lista de países, disciplinas y atletas.
from .countries import COUNTRY_CHOICES
from .disciplines import DISCIPLINE_CHOICES
from .branches import BRANCH_CHOICES

# Modelo para representar los equipos olímpicos
class OlympicTeam(models.Model):
    olympic_country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    discipline = models.CharField(max_length=100, choices=DISCIPLINE_CHOICES)
    branch = models.CharField(max_length=100)
    team_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('olympic_country', 'discipline', 'branch')

    def __str__(self):
        return f"{self.team_name} - {self.olympic_country}"

class Profile(models.Model):
    ROLE_CHOICES = [
        ('Athlete', 'Atleta'),
        ('Coach', 'Coach'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES, blank=True)
    olympic_country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    discipline = models.CharField(max_length=100, choices=DISCIPLINE_CHOICES)
    branch = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=50, choices=[('Athlete', 'Atleta'), ('Coach', 'Coach')], default='Athlete')
    olympic_team = models.ForeignKey(OlympicTeam, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members')
    security_answer1 = models.CharField(max_length=255, blank=True, null=True)
    security_answer2 = models.CharField(max_length=255, blank=True, null=True)
    security_answer3 = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} - {self.discipline} ({self.branch})'

    def is_coach(self):
        return self.role == 'Coach'

    def is_athlete(self):
        return self.role == 'Athlete'

    def assign_to_team(self):
        # Asignación automática de equipo olímpico basado en país, disciplina y rama
        team, created = OlympicTeam.objects.get_or_create(
            olympic_country=self.olympic_country,
            discipline=self.discipline,
            branch=self.branch,
            defaults={'team_name': f"Equipo {self.olympic_country} de {self.discipline} - {self.branch}"}
        )
        self.olympic_team = team
        self.save()

class SubTeam(models.Model):
    name = models.CharField(max_length=100, unique=True)
    team = models.ForeignKey(OlympicTeam, on_delete=models.CASCADE, related_name="subteams")
    coaches = models.ManyToManyField(Profile, limit_choices_to={'role': 'Coach'}, related_name="subteams_coaches")
    athletes = models.ManyToManyField(Profile, limit_choices_to={'role': 'Athlete'}, related_name="subteams_athletes")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.team}"

    def can_add_coach(self):
        """Verifica si puede agregar otro coach (máximo 3)"""
        return self.coaches.count() < 3

    # Método para verificar si un atleta puede ser asignado a más de dos subequipos
    def can_add_athlete(self, athlete):
        if athlete.subteams_athletes.count() >= 2:
            return False
        return True
    def can_remove_athlete(self, athlete):
        """Verifica si se puede remover a un atleta del subequipo"""
        return self.athletes.filter(id=athlete.id).exists()

    def can_add_more_subteams(self, coach):
        """Verifica si el coach puede tener más subequipos (máximo 4)"""
        return coach.subteams_coaches.count() < 4

# Modelo para los récords confidenciales de los atletas
class AthleteRecord(models.Model):
    athlete = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='athlete_records')
    coach = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='coach_records')
    evaluation_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  
    
    def __str__(self):
        return f"Evaluación de {self.athlete.user.username} por {self.coach.user.username} el {self.evaluation_date}"
    
    def total_score(self):
        # Este método suma todas las puntuaciones de los criterios asociados a este registro.
        return self.criteria.aggregate(Sum('score'))['score__sum'] or 0

# Modelo para los criterios de evaluación de los atletas
class EvaluationCriterion(models.Model):
    athlete_record = models.ForeignKey(AthleteRecord, on_delete=models.CASCADE, related_name='criteria')
    criterion_name = models.CharField(max_length=255)  # Nombre del criterio (Dificultad, Sincronización, etc.)
    score = models.IntegerField(choices=[(i, i) for i in range(1, 11)])  # Puntuación del 1 al 10
    notes = models.TextField(max_length=255, blank=True, null=True)  # Notas opcionales
    
    def __str__(self):
        return f"{self.criterion_name}: {self.score} puntos"
    
    def total_score(self):
        return self.criteria.aggregate(Sum('score'))['score__sum'] or 0


