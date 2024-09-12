from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_last_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    country = models.CharField(max_length=100)
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    role = models.CharField(max_length=50, choices=[('Athlete', 'Athlete'), ('Coach', 'Coach')])

    def __str__(self):
        return f'{self.user.username} Profile'