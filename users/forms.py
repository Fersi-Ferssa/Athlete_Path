from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, AthleteRecord
# Importa la lista de países, disciplinas y atletas.
from .countries import COUNTRY_CHOICES
from .disciplines import DISCIPLINE_CHOICES
from .branches import BRANCH_CHOICES

# FORMULARIO DE REGISTRO DE USUARIOS
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label="Correo electrónico")
    first_name = forms.CharField(max_length=50, label="Primer Nombre")
    last_name = forms.CharField(max_length=50, label="Primer Apellido")
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=range(1966, 2012)), label="Fecha de nacimiento")
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, label="País de nacimiento")
    sex = forms.ChoiceField(choices=[('Male', 'Masculino'), ('Female', 'Femenino')], label="Sexo")
    role = forms.ChoiceField(choices=[('Athlete', 'Atleta'), ('Coach', 'Entrenador')], label="Rol")
    security_answer1 = forms.CharField(max_length=255, label="¿Cuál es tu color favorito?")
    security_answer2 = forms.CharField(max_length=255, label="¿Cuál es el apodo de tu mejor amigo?")
    security_answer3 = forms.CharField(max_length=255, label="¿Cuál es tu película favorita?")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'date_of_birth', 'country', 'sex', 'role', 'password1', 'password2', 'security_answer1','security_answer2', 'security_answer3']
        labels = {
            'username': "Nombre de usuario",
            'password1': "Contraseña",
            'password2': "Confirmación de contraseña",
        }

# Formulario para el perfil del usuario (atleta o coach)
class ProfileForm(forms.ModelForm):
    olympic_country = forms.ChoiceField(choices=COUNTRY_CHOICES, label="País olímpico")
    discipline = forms.ChoiceField(choices=DISCIPLINE_CHOICES, label="Disciplina")
    branch = forms.ChoiceField(choices=[], label="Rama", required=False)  # Inicialmente vacío

    class Meta:
        model = Profile
        fields = ['olympic_country', 'discipline', 'branch', 'team_name']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        discipline_selected = self.data.get('discipline') or self.initial.get('discipline')
        if discipline_selected:
            self.fields['branch'].choices = BRANCH_CHOICES.get(discipline_selected, [])
        else:
            self.fields['branch'].choices = []

# Formulario para que el coach pueda editar el nombre del equipo
class TeamNameForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['team_name']
        labels = {
            'team_name': 'Nombre del Equipo',
        }

class AthleteRecordForm(forms.ModelForm):
    evaluation_date = forms.DateField(
    widget=forms.SelectDateWidget(years=range(2000, 2025)),
    label="Fecha de Evaluación",
    required=True
)


    class Meta:
        model = AthleteRecord
        fields = ['difficulty', 'execution', 'notes', 'evaluation_date']  # Añadimos el nuevo campo
        labels = {
            'difficulty': 'Dificultad',
            'execution': 'Ejecución',
            'notes': 'Notas',
            'evaluation_date': 'Fecha de Evaluación',
        }

class ResetPasswordForm(forms.Form):
    username = forms.CharField(max_length=150, label="Nombre de usuario")
    security_answer = forms.CharField(max_length=100, label="Nombre de tu primera mascota")
    new_password = forms.CharField(widget=forms.PasswordInput, label="Nueva contraseña")
