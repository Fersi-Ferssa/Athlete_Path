from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, AthleteRecord, SubTeam, EvaluationCriterion
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
        fields = ['username', 'email', 'first_name', 'last_name', 'date_of_birth', 'country', 'sex', 'role', 'password1', 'password2', 'security_answer1', 'security_answer2', 'security_answer3']
        labels = {
            'username': "Nombre de usuario",
            'password1': "Contraseña",
            'password2': "Confirmación de contraseña",
        }

# FORMULARIO DEL PERFIL DE USUARIOS (ATLETAS/COACHES)
class ProfileForm(forms.ModelForm):
    olympic_country = forms.ChoiceField(choices=COUNTRY_CHOICES, label="País olímpico")
    discipline = forms.ChoiceField(choices=DISCIPLINE_CHOICES, label="Disciplina")
    branch = forms.ChoiceField(choices=[], label="Rama", required=False)

    class Meta:
        model = Profile
        fields = ['olympic_country', 'discipline', 'branch']

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        discipline_selected = self.data.get('discipline') or self.initial.get('discipline')
        if discipline_selected:
            self.fields['branch'].choices = BRANCH_CHOICES.get(discipline_selected, [])
        else:
            self.fields['branch'].choices = []

# FORMULARIO DE SUBEQUIPOS
class SubTeamForm(forms.ModelForm):
    class Meta:
        model = SubTeam
        fields = ['name', 'athletes']
        labels = {
            'name': 'Nombre del Subequipo',
            'athletes': 'Seleccionar Atletas',
        }

    def clean_athletes(self):
        athletes = self.cleaned_data.get('athletes')
        if athletes:
            for athlete in athletes:
                if SubTeam.objects.filter(athletes=athlete).exists():
                    raise forms.ValidationError(f"{athlete.user.first_name} ya está en un subequipo.")
        return athletes

# FORMULARIO DE REGISTROS/VALUACIONES
class AthleteRecordForm(forms.ModelForm):
    evaluation_date = forms.DateField(widget=forms.SelectDateWidget(years=range(2000, 2025)))

    class Meta:
        model = AthleteRecord
        fields = ['evaluation_date']

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

# FORMULARIO DE RESET DE CONTRASEÑA
class ResetPasswordForm(forms.Form):
    username = forms.CharField(max_length=150, label="Nombre de usuario")
    security_answer = forms.CharField(max_length=100, label="Nombre de tu primera mascota")
    new_password = forms.CharField(widget=forms.PasswordInput, label="Nueva contraseña")