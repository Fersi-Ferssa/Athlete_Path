from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, ProfileForm, AthleteRecordForm
from .models import Profile, AthleteRecord


@login_required
def home(request):
    profile = request.user.profile
    # Redirigir según el tipo de perfil (Atleta o Coach)
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
        athletes = Profile.objects.filter(olympic_country=profile.olympic_country, discipline=profile.discipline, branch=profile.branch)
        return render(request, 'coach_dashboard.html', {'profile': profile, 'athletes': athletes})
    return redirect('home')

@login_required
def athlete_profile(request):
    profile = request.user.profile
    # Mostrar el perfil del atleta y sus registros
    if profile.is_athlete():
        records = AthleteRecord.objects.filter(athlete=profile)
        return render(request, 'athlete_profile.html', {'profile': profile, 'records': records})
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
