from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, ProfileForm, AthleteRecordForm
from .models import Profile

@login_required
def home(request):
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
            profile.save()
            return redirect('login')
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
def add_record(request):
    if request.method == 'POST':
        record_form = AthleteRecordForm(request.POST)
        if record_form.is_valid():
            record_form.save()
            return redirect('home')
    else:
        record_form = AthleteRecordForm()
    return render(request, 'add_record.html', {'form': record_form})

@login_required
def view_athlete_records(request, athlete_id):
    athlete = Profile.objects.get(id=athlete_id, role='Atleta')
    records = AthleteRecord.objects.filter(athlete=athlete)
    return render(request, 'view_records.html', {'athlete': athlete, 'records': records})
