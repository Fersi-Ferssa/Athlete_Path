from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required  # Decorador para proteger vistas que requieren que el usuario esté logueado
from django.contrib.auth import login, authenticate  # Métodos para autenticar y loguear a usuarios
from django.contrib import messages  # Biblioteca para manejar mensajes flash en las vistas
from django import forms  # Importación del módulo de formularios de Django
from .models import Profile  # Importa el modelo Profile
from .forms import UserRegisterForm, ProfileForm  # Importa los formularios de registro de usuario y perfil

@login_required
def home(request):
    """
    Vista para la página de inicio (home) que requiere que el usuario esté autenticado.
    Muestra un mensaje de bienvenida con el nombre de usuario actual.
    """
    return render(request, 'home.html', {'username': request.user.username})  # Pasa el nombre de usuario al template 'home.html'

def register(request):
    """
    Vista para el registro de usuarios, que maneja tanto la creación del usuario como el perfil.
    """
    if request.method == 'POST':  # Si el formulario fue enviado (método POST)
        user_form = UserRegisterForm(request.POST)  # Crea una instancia de UserRegisterForm con los datos enviados
        profile_form = ProfileForm(request.POST)  # Crea una instancia de ProfileForm con los datos enviados
        if user_form.is_valid() and profile_form.is_valid():  # Valida ambos formularios
            # Guardar el usuario
            user = user_form.save()  # Guarda el formulario del usuario en la base de datos
            # Guardar el perfil y vincularlo con el usuario
            profile = profile_form.save(commit=False)  # No guarda aún el perfil hasta vincularlo con el usuario
            profile.user = user  # Asigna el usuario recién creado al perfil
            profile.save()  # Guarda el perfil en la base de datos
            return redirect('login')  # Redirige al login una vez que el registro ha sido exitoso
    else:
        user_form = UserRegisterForm()  # Si no es POST, crea un formulario en blanco
        profile_form = ProfileForm()  # Crea el formulario en blanco para el perfil

    # Renderiza la página de registro con ambos formularios: user_form y profile_form
    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})

class ProfileForm(forms.ModelForm):
    """
    Formulario para manejar la creación y actualización del perfil de usuario.
    Está vinculado al modelo Profile y permite seleccionar campos como primer apellido, fecha de nacimiento, país, sexo y rol.
    """
    class Meta:
        model = Profile  # Define que el formulario está vinculado al modelo Profile
        fields = ['first_last_name', 'date_of_birth', 'country', 'sex', 'role']  # Campos que se mostrarán en el formulario
        widgets = {
            'first_last_name': forms.TextInput(),  # Widget de entrada de texto para el apellido
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),  # Widget de selección de fecha
            'sex': forms.Select(),  # Widget desplegable para seleccionar el sexo
            'role': forms.Select(),  # Widget desplegable para seleccionar el rol
        }

def user_login(request):
    """
    Vista para el inicio de sesión de los usuarios.
    Si las credenciales son correctas, redirige al home; de lo contrario, muestra un mensaje de error.
    """
    if request.method == 'POST':  # Si el formulario fue enviado (método POST)
        username = request.POST['username']  # Obtiene el nombre de usuario del formulario
        password = request.POST['password']  # Obtiene la contraseña del formulario
        user = authenticate(request, username=username, password=password)  # Autentica el usuario
        if user is not None:  # Si el usuario fue autenticado correctamente
            login(request, user)  # Loguea al usuario
            return redirect('home')  # Redirige a la página de inicio
        else:
            messages.error(request, 'Username or password incorrect')  # Muestra un mensaje de error si las credenciales no son correctas
    return render(request, 'login.html')  # Renderiza la página de login si no es POST o si hubo un error

@login_required
def home(request):
    """
    Vista de inicio protegida que solo puede ser accedida por usuarios logueados.
    """
    return render(request, 'home.html')  # Renderiza el template 'home.html'