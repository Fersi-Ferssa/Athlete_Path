from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash  # Corrección de la importación
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import UserRegisterForm, ProfileForm, AthleteRecordForm, TeamNameForm, ResetPasswordForm
from .models import Profile, AthleteRecord

@login_required
def home(request):
    profile = request.user.profile
    # Redirigir según el tipo de perfil
    if profile.is_coach():
        return redirect('coach_dashboard')
    elif profile.is_athlete():
        return redirect('athlete_profile')
    return render(request, 'home.html', {'username': request.user.username})

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            # Guardar el usuario
            user = user_form.save()
            # Guardar el perfil
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.role = user_form.cleaned_data['role']  # Asignar el rol seleccionado en el formulario
            profile.security_answer = user_form.cleaned_data['security_answer']  # Guardar la respuesta de seguridad
            profile.save()
            return redirect('login')
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        user_form = UserRegisterForm()
        profile_form = ProfileForm()

    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    return render(request, 'login.html')

@login_required
def coach_dashboard(request):
    profile = request.user.profile

    # Verificar si es coach y obtener los atletas del mismo equipo
    if profile.is_coach():
        athletes = Profile.objects.filter(
            olympic_country=profile.olympic_country, 
            discipline=profile.discipline, 
            branch=profile.branch
        ).exclude(user=request.user)  # Excluimos al coach de la lista de atletas

        # Procesar el formulario para editar el nombre del equipo
        if request.method == 'POST':
            team_form = TeamNameForm(request.POST, instance=profile)
            if team_form.is_valid():
                team_form.save()
                messages.success(request, 'El nombre del equipo ha sido actualizado.')
                return redirect('coach_dashboard')
        else:
            team_form = TeamNameForm(instance=profile)

        return render(request, 'coach_dashboard.html', {
            'profile': profile,
            'athletes': athletes,
            'team_form': team_form  # Pasar el formulario al template
        })

    return redirect('home')

@login_required
def athlete_profile(request):
    profile = request.user.profile
    
    # Verificamos que el usuario es un atleta
    if profile.is_athlete():
        # Obtenemos todas las evaluaciones del atleta ordenadas por la fecha de evaluación
        records = AthleteRecord.objects.filter(athlete=profile).select_related('coach').order_by('-evaluation_date')
        
        # Tomamos el equipo actual desde el perfil del coach más reciente
        if records.exists():
            team_name = records.first().coach.team_name  # Obtenemos el último equipo asignado por el coach
        else:
            team_name = "Sin equipo asignado"

        return render(request, 'athlete_profile.html', {
            'profile': profile,
            'records': records,
            'team_name': team_name,
        })
    return redirect('home')

@login_required
def add_record(request):
    if request.method == 'POST':
        record_form = AthleteRecordForm(request.POST)
        if record_form.is_valid():
            record = record_form.save(commit=False)
            record.coach = request.user.profile
            record.save()
            return redirect('coach_dashboard')
    else:
        record_form = AthleteRecordForm()
    return render(request, 'add_record.html', {'form': record_form})

@login_required
def evaluate_athlete(request, athlete_id):
    athlete = get_object_or_404(Profile, id=athlete_id, role='Athlete')

    # Solo permitir evaluación por coaches del mismo equipo
    if request.user.profile.is_coach() and athlete.olympic_country == request.user.profile.olympic_country:
        if request.method == 'POST':
            form = AthleteRecordForm(request.POST)
            if form.is_valid():
                record = form.save(commit=False)
                record.athlete = athlete
                record.coach = request.user.profile
                record.evaluation_date = form.cleaned_data['evaluation_date']  # Guardar la fecha de evaluación
                record.save()
                messages.success(request, 'Evaluación guardada con éxito.')
                return redirect('coach_dashboard')
        else:
            form = AthleteRecordForm()
        return render(request, 'evaluate_athlete.html', {'form': form, 'athlete': athlete})
    else:
        messages.error(request, 'No tienes permiso para evaluar a este atleta.')
        return redirect('home')

@login_required
def view_athlete_records(request, athlete_id):
    athlete = get_object_or_404(Profile, id=athlete_id, role='Athlete')
    records = AthleteRecord.objects.filter(athlete=athlete)
    return render(request, 'view_records.html', {'athlete': athlete, 'records': records})

def password_reset_view(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            security_answer = form.cleaned_data['security_answer']
            new_password = form.cleaned_data['new_password']

            try:
                # Verificar si el usuario existe
                user = User.objects.get(username=username)
                
                # Verificar si el perfil existe
                profile = getattr(user, 'profile', None)

                if profile is None:
                    messages.error(request, 'No se encontró un perfil asociado a este usuario.')
                    return render(request, 'reset_password.html', {'form': form})

                # Verificar la respuesta de seguridad
                if profile.security_answer and profile.security_answer.lower() == security_answer.lower():
                    user.set_password(new_password)
                    user.save()

                    # Mantener la sesión activa con la nueva contraseña
                    update_session_auth_hash(request, user)

                    messages.success(request, 'La contraseña ha sido cambiada exitosamente.')
                    return redirect('login')  # Redirigir al login después del cambio de contraseña
                else:
                    messages.error(request, 'La respuesta de seguridad es incorrecta.')
            except User.DoesNotExist:
                messages.error(request, 'El nombre de usuario no existe.')
    else:
        form = ResetPasswordForm()

    return render(request, 'reset_password.html', {'form': form})