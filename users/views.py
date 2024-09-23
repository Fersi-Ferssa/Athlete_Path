from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Max, ExpressionWrapper, F, IntegerField, Count
from django.contrib import messages
from .forms import UserRegisterForm, ProfileForm, AthleteRecordForm, TeamNameForm, ResetPasswordForm
from .models import Profile, AthleteRecord

@login_required
def home(request):
    profile = request.user.profile
    full_name = f"{profile.user.first_name} {profile.user.last_name}"
    # Redirigir según el tipo de perfil
    if profile.is_coach():
        return redirect('coach_dashboard')
    elif profile.is_athlete():
        return redirect('athlete_profile')
    return render(request, 'home.html', {'full_name': full_name})

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
            profile.role = user_form.cleaned_data['role']
            profile.security_answer = user_form.cleaned_data['security_answer']
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
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    return render(request, 'login.html')

@login_required
def athlete_profile(request):
    profile = request.user.profile
    full_name = f"{profile.user.first_name} {profile.user.last_name}"
    
    if profile.is_athlete():
        # Obtener la última evaluación del atleta actual
        latest_record = AthleteRecord.objects.filter(athlete=profile).order_by('-evaluation_date').first()

        # Obtener el nombre del equipo del coach
        coach = Profile.objects.filter(
            role='Coach',
            discipline=profile.discipline,
            branch=profile.branch
        ).first()

        team_name = coach.team_name if coach else 'No asignado'

        # Obtener los mejores atletas en la misma disciplina y rama (sin usar distinct)
        best_athletes = Profile.objects.filter(
            discipline=profile.discipline,
            branch=profile.branch,
            role='Athlete'
        ).annotate(
            max_score=Max(F('athlete_records__difficulty') + F('athlete_records__execution'))
        ).order_by('-max_score')[:5]

        # Campeones "Ganadora Olimpiadas París 2024"
        champions = {
            'Uneven Bars': {'name': 'Rebeca Andrade', 'country': 'Brasil', 'difficulty': 6, 'execution': 8, 'score': 14},
            'Floor': {'name': 'Ana Barbosu', 'country': 'Rumania', 'difficulty': 5, 'execution': 7, 'score': 12},
            'Balance Beam': {'name': 'Luisa Blanco', 'country': 'Colombia', 'difficulty': 5, 'execution': 7, 'score': 12},
        }
        champion = champions.get(profile.branch, None)

        # Formulario de cambio de contraseña
        if request.method == 'POST':
            form = PasswordChangeForm(user=request.user, data=request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
                return redirect('athlete_profile')
        else:
            form = PasswordChangeForm(user=request.user)

        return render(request, 'athlete_profile.html', {
            'profile': profile,
            'full_name': full_name,
            'latest_record': latest_record,
            'best_athletes': best_athletes,
            'champion': champion,
            'team_name': team_name,
            'form': form
        })
    return redirect('home')

@login_required
def coach_dashboard(request):
    profile = request.user.profile
    full_name = f"{profile.user.first_name} {profile.user.last_name}"

    # Verificar si es coach y obtener los atletas del mismo equipo
    if profile.is_coach():
        athletes = Profile.objects.filter(
            olympic_country=profile.olympic_country, 
            discipline=profile.discipline, 
            branch=profile.branch
        ).exclude(user=request.user)

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
            'full_name': full_name,
            'athletes': athletes,
            'team_form': team_form
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
    full_name = f"{athlete.user.first_name} {athlete.user.last_name}"

    # Solo permitir evaluación por coaches del mismo equipo
    if request.user.profile.is_coach() and athlete.olympic_country == request.user.profile.olympic_country:
        if request.method == 'POST':
            form = AthleteRecordForm(request.POST)
            if form.is_valid():
                record = form.save(commit=False)
                record.athlete = athlete
                record.coach = request.user.profile
                record.evaluation_date = form.cleaned_data['evaluation_date']
                record.save()
                messages.success(request, 'Evaluación guardada con éxito.')
                return redirect('coach_dashboard')
        else:
            form = AthleteRecordForm()
        return render(request, 'evaluate_athlete.html', {'form': form, 'athlete': athlete, 'full_name': full_name})
    else:
        messages.error(request, 'No tienes permiso para evaluar a este atleta.')
        return redirect('home')

@login_required
def view_athlete_records(request, athlete_id):
    athlete = get_object_or_404(Profile, id=athlete_id, role='Athlete')
    full_name = f"{athlete.user.first_name} {athlete.user.last_name}"
    records = AthleteRecord.objects.filter(athlete=athlete)
    return render(request, 'view_records.html', {'athlete': athlete, 'full_name': full_name, 'records': records})

def password_reset_view(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            security_answer = form.cleaned_data['security_answer']
            new_password = form.cleaned_data['new_password']

            try:
                user = User.objects.get(username=username)
                profile = getattr(user, 'profile', None)

                if profile is None:
                    messages.error(request, 'No se encontró un perfil asociado a este usuario.')
                    return render(request, 'reset_password.html', {'form': form})

                if profile.security_answer and profile.security_answer.lower() == security_answer.lower():
                    user.set_password(new_password)
                    user.save()

                    update_session_auth_hash(request, user)

                    messages.success(request, 'La contraseña ha sido cambiada exitosamente.')
                    return redirect('login')
                else:
                    messages.error(request, 'La respuesta de seguridad es incorrecta.')
            except User.DoesNotExist:
                messages.error(request, 'El nombre de usuario no existe.')
    else:
        form = ResetPasswordForm()

    return render(request, 'reset_password.html', {'form': form})

@login_required
def comparison_options(request):
    profile = request.user.profile

    if profile.is_athlete():
        if request.method == 'POST':
            comparison_type = request.POST.get('comparison_type')
            
            if comparison_type == 'personal_records':
                return redirect('compare_personal_records')
            elif comparison_type == 'other_athletes':
                return redirect('compare_with_athletes')

        return render(request, 'comparison_options.html')
    return redirect('home')

@login_required
def compare_personal_records(request):
    profile = request.user.profile
    
    if profile.is_athlete():
        personal_records = AthleteRecord.objects.filter(athlete=profile).order_by('-evaluation_date')
        
        if request.method == 'POST':
            record_1_id = request.POST.get('record_1')
            record_2_id = request.POST.get('record_2')
            
            if not record_1_id or not record_2_id:
                messages.error(request, 'Por favor selecciona dos récords diferentes para comparar.')
                return render(request, 'compare_personal_records.html', {'records': personal_records})
            
            if record_1_id == record_2_id:
                messages.error(request, 'No puedes comparar el mismo récord.')
                return render(request, 'compare_personal_records.html', {'records': personal_records})

            record_1 = get_object_or_404(AthleteRecord, id=record_1_id)
            record_2 = get_object_or_404(AthleteRecord, id=record_2_id)

            return render(request, 'compare_personal_records_result.html', {
                'record_1': record_1,
                'record_2': record_2,
            })

        return render(request, 'compare_personal_records.html', {'records': personal_records})
    return redirect('home')

@login_required
def compare_with_athletes(request):
    profile = request.user.profile
    
    if profile.is_athlete():
        # Obtener todos los atletas de la misma disciplina y rama
        other_athletes = Profile.objects.filter(
            discipline=profile.discipline,
            branch=profile.branch,
            role='Athlete'
        ).exclude(user=request.user)

        if request.method == 'POST':
            selected_athlete_id = request.POST.get('selected_athlete')
            
            if not selected_athlete_id:
                messages.error(request, 'Por favor selecciona un atleta para comparar.')
                return render(request, 'compare_with_athletes.html', {'athletes': other_athletes})
            
            selected_athlete = get_object_or_404(Profile, id=selected_athlete_id)
            
            # Obtener el último registro del atleta actual y el seleccionado
            current_athlete_record = AthleteRecord.objects.filter(athlete=profile).order_by('-evaluation_date').first()
            selected_athlete_record = AthleteRecord.objects.filter(athlete=selected_athlete).order_by('-evaluation_date').first()

            # Verificar si se encontraron registros
            if not current_athlete_record:
                messages.error(request, 'No tienes registros disponibles para comparar.')
                return redirect('comparison_options')

            if not selected_athlete_record:
                messages.error(request, 'El atleta seleccionado no tiene registros disponibles para comparar.')
                return redirect('comparison_options')

            # Calcular la diferencia de puntos y el valor absoluto
            current_score = current_athlete_record.total_score()
            selected_score = selected_athlete_record.total_score()
            score_difference = current_score - selected_score
            abs_difference = abs(score_difference)  # Calcular el valor absoluto

            return render(request, 'compare_with_athletes_result.html', {
                'athlete': profile,
                'athlete_record': current_athlete_record,
                'compare_athlete': selected_athlete,
                'compare_record': selected_athlete_record,
                'score_difference': score_difference,
                'abs_difference': abs_difference  # Enviar el valor absoluto a la plantilla
            })

        return render(request, 'compare_with_athletes.html', {'athletes': other_athletes})
    return redirect('home')