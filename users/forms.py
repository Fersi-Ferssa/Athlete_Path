from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, AthleteRecord
from .countries import COUNTRY_CHOICES  # Importa la lista de países

# Formulario de registro para usuarios
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Correo electrónico")
    first_name = forms.CharField(max_length=50, label="Primer Nombre")
    last_name = forms.CharField(max_length=50, label="Primer Apellido")
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=range(1966, 2012)), label="Fecha de nacimiento")
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, label="País de nacimiento")
    sex = forms.ChoiceField(choices=[('Male', 'Masculino'), ('Female', 'Femenino')], label="Sexo")
    role = forms.ChoiceField(choices=[('Athlete', 'Atleta'), ('Coach', 'Entrenador')], label="Rol")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'date_of_birth', 'country', 'sex', 'role', 'password1', 'password2']
        labels = {
            'username': "Nombre de usuario",
            'password1': "Contraseña",
            'password2': "Confirmación de contraseña",
        }

# Formulario para el perfil del usuario (atleta o coach)
class ProfileForm(forms.ModelForm):
    olympic_country = forms.ChoiceField(choices=COUNTRY_CHOICES, label="País olímpico")
    discipline = forms.ChoiceField(choices=[('Gymnastics', 'Gimnasia Artística')], label="Disciplina")
    branch = forms.ChoiceField(choices=[
        ('Uneven Bars', 'Barras Asimétricas'),
        ('Balance Beam', 'Barra de Equilibrio'),
        ('Floor', 'Piso')
    ], label="Rama")
    team_name = forms.CharField(max_length=100, label="Nombre del equipo", required=False)

    class Meta:
        model = Profile
        fields = ['olympic_country', 'discipline', 'branch', 'team_name']

# Formulario para la evaluación de los atletas por los entrenadores
class AthleteRecordForm(forms.ModelForm):
    class Meta:
        model = AthleteRecord
        fields = ['athlete', 'difficulty', 'execution', 'notes']
        labels = {
            'difficulty': 'Dificultad',
            'execution': 'Ejecución',
            'notes': 'Notas',
        }
