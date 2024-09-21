from django import forms  # Importa el módulo de formularios de Django
from django.contrib.auth.forms import UserCreationForm  # Importa el formulario de creación de usuarios predeterminado de Django
from django.contrib.auth.models import User  # Importa el modelo de usuarios de Django
from .models import Profile  # Importa el modelo de perfil personalizado
from .countries import COUNTRY_CHOICES  # Importa la lista de opciones de países

# Definición del formulario para el registro de usuarios, basado en el formulario predeterminado de Django.
class UserRegisterForm(UserCreationForm):
    # Campo para el correo electrónico, es obligatorio en el formulario
    email = forms.EmailField()
    
    # Campo para el nombre del usuario
    name = forms.CharField(max_length=100)
    
    # Campo para el primer apellido
    first_last_name = forms.CharField(max_length=100)
    
    # Campo para la fecha de nacimiento, con un widget de selección de fecha que muestra un rango de años
    date_of_birth = forms.DateField(widget=forms.SelectDateWidget(years=range(1966, 2012)))
    
    # Campo para seleccionar el país, utilizando una lista de opciones definida en 'COUNTRY_CHOICES'
    country = forms.ChoiceField(choices=COUNTRY_CHOICES)
    
    # Campo para seleccionar el sexo, con dos opciones ('Male', 'Female')
    sex = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')])
    
    # Campo para seleccionar el rol del usuario, ya sea 'Athlete' o 'Coach'
    role = forms.ChoiceField(choices=[('Athlete', 'Athlete'), ('Coach', 'Coach')])

    # Definición de los metadatos del formulario, asociando el formulario con el modelo User y especificando los campos que deben estar presentes
    class Meta:
        model = User  # El formulario se basa en el modelo 'User'
        fields = ['username', 'email', 'name', 'first_last_name', 'date_of_birth', 'country', 'sex', 'role', 'password1', 'password2']
        # Incluye todos los campos del formulario que el usuario debe completar, incluyendo los campos de contraseña para la validación y registro.

# Formulario para el modelo 'Profile', que contiene información adicional del usuario registrada en el modelo 'Profile'.
class ProfileForm(forms.ModelForm):
    # Los campos y widgets que se utilizarán para el formulario de perfil del usuario.
    class Meta:
        model = Profile  # Asocia el formulario con el modelo 'Profile'
        fields = ['first_last_name', 'date_of_birth', 'country', 'sex', 'role']  # Campos que serán utilizados en el formulario.
        
        # Widgets personalizados para cada campo, para mejorar la experiencia de usuario
        widgets = {
            'first_last_name': forms.TextInput(attrs={'placeholder': 'Introduce tu apellido'}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),  # Utiliza un campo de fecha
            'sex': forms.Select(),  # Selección desplegable para 'sexo'
            'role': forms.Select(),  # Selección desplegable para 'rol'
        }
    
    # Campo para seleccionar el país, usando nuevamente la lista de opciones de países
    country = forms.ChoiceField(choices=COUNTRY_CHOICES)