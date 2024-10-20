from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Max, F
from django.contrib import messages
from .forms import UserRegisterForm, ProfileForm, AthleteRecordForm, ResetPasswordForm, SubTeamForm
from .models import Profile, AthleteRecord, OlympicTeam, SubTeam, EvaluationCriterion
from django.http import JsonResponse
from .branches import BRANCH_CHOICES
import json
from django.conf import settings
from django.http import JsonResponse
from django.contrib import messages
from .countries import COUNTRY_CHOICES
from .disciplines import DISCIPLINE_CHOICES  # Importa las disciplinas
from .branches import BRANCH_CHOICES  # Importa las ramas

####################################################################################################
#                                       MAIN HOME PAGE                                             #
####################################################################################################

# MAIN HOME PAGE
def home(request):
    countries = COUNTRY_CHOICES
    disciplines = DISCIPLINE_CHOICES
    return render(request, 'home.html', {
        'countries': countries,
        'disciplines': disciplines
    })

# OBTAIN THE DISCIPLINES BRANCHES
def get_branches(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            discipline = data.get('discipline')
            branches = BRANCH_CHOICES.get(discipline, [])
            return JsonResponse({'branches': branches})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

# VIEW OLYMPIC TEAMS
def view_team(request):
    country = request.GET.get('country')
    discipline = request.GET.get('discipline')
    branch = request.GET.get('branch')

    # Filtrar el equipo olímpico basado en país, disciplina y rama
    team = OlympicTeam.objects.filter(
        olympic_country=country,
        discipline=discipline,
        branch=branch
    ).first()

    if team:
        # Obtener todos los atletas y coaches del equipo
        coaches = Profile.objects.filter(olympic_team=team, role='Coach')
        athletes = Profile.objects.filter(olympic_team=team, role='Athlete')
    else:
        coaches = []
        athletes = []

    return render(request, 'view_team.html', {
        'team': team,
        'coaches': coaches,
        'athletes': athletes
    })

####################################################################################################
#                                       GENERAL ASPECTS                                            #
####################################################################################################

# REGISTER
def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Guardar el usuario
            user = user_form.save()

            # Crear el perfil
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.date_of_birth = user_form.cleaned_data['date_of_birth']
            profile.country = user_form.cleaned_data['country']
            profile.role = user_form.cleaned_data['role']
            profile.security_answer1 = user_form.cleaned_data['security_answer1']
            profile.security_answer2 = user_form.cleaned_data['security_answer2']
            profile.security_answer3 = user_form.cleaned_data['security_answer3']

            # Asignar automáticamente al equipo olímpico
            profile.assign_to_team()
            profile.save()

            # Iniciar sesión y redirigir
            login(request, user)
            messages.success(request, "Registro completado y asignado a equipo olímpico.")
            return redirect('login')
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        user_form = UserRegisterForm()
        profile_form = ProfileForm()

    return render(request, 'register.html', {'user_form': user_form, 'profile_form': profile_form})

def get_branches(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)  # Capturamos el JSON del cuerpo de la solicitud
            discipline = data.get('discipline')  # Obtenemos la disciplina seleccionada
            branches = BRANCH_CHOICES.get(discipline, [])  # Obtenemos las ramas para esa disciplina
            return JsonResponse({'branches': branches})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=400)

# LOGIN
def user_login(request):
    # Limpiar cualquier mensaje anterior cuando se accede a la página de login
    storage = messages.get_messages(request)
    storage.used = True  # Marcar mensajes como usados para que no se arrastren

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            # Si el usuario no se autentica, mostrar el error solo en esta vista
            messages.set_level(request, messages.ERROR)
            messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
            return render(request, 'login.html')

    return render(request, 'login.html')

def clean_messages(request):
    """
    Elimina los mensajes almacenados en la sesión de la solicitud actual.
    """
    storage = messages.get_messages(request)
    for message in storage:
        pass  # Marca todos los mensajes como "usados"

# PASSWORD RESET
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

####################################################################################################
#                                       COACH                                                      #
####################################################################################################

# COACH PROFILE
@login_required
def coach_profile(request):
    profile = request.user.profile
    return render(request, 'profile.html', {'profile': profile})

# COACH DASHBOARD
@login_required
def coach_dashboard(request):
    profile = request.user.profile

    if profile.is_coach():
        # Obtener el equipo olímpico del coach
        olympic_team = profile.olympic_team

        # Obtener todos los subequipos en los que el coach participa
        subteams = SubTeam.objects.filter(coaches=profile)

        return render(request, 'coach_dashboard.html', {
            'profile': profile,
            'olympic_team': olympic_team,
            'subteams': subteams,
        })

    return redirect('home')

# CREATE SUBTEAM
@login_required
def create_subteam(request):
    profile = request.user.profile

    if not profile.is_coach():
        return redirect('home')

    # Verificar si el coach tiene un equipo olímpico asignado
    if not profile.olympic_team:
        messages.error(request, "No tienes un equipo olímpico asignado.")
        return redirect('manage_subteams')

    # Verificar si el coach puede crear más subequipos
    if SubTeam.objects.filter(coaches=profile).count() >= 4:
        messages.error(request, "No puedes crear más de 4 subequipos.")
        return redirect('manage_subteams')

    # Obtener atletas disponibles antes de manejar el método POST
    available_athletes = Profile.objects.filter(
        olympic_team=profile.olympic_team,
        role='Athlete'
    ).exclude(subteams_athletes__isnull=False)

    if request.method == 'POST':
        subteam_form = SubTeamForm(request.POST)
        if subteam_form.is_valid():
            # Crear el subequipo sin guardar aún
            subteam = subteam_form.save(commit=False)
            # Asignar el equipo olímpico al subequipo
            subteam.team = profile.olympic_team
            subteam.save()
            subteam.coaches.add(profile)  # Añadir el coach creador

            # Asignar los atletas seleccionados al subequipo
            athletes_selected = request.POST.getlist('athletes')
            for athlete_id in athletes_selected:
                athlete = Profile.objects.get(id=athlete_id)
                # Verificar que el atleta pertenezca al mismo equipo olímpico
                if athlete.olympic_team == profile.olympic_team:
                    subteam.athletes.add(athlete)
                else:
                    messages.error(request, f"{athlete.user.first_name} no pertenece al equipo olímpico correcto.")

            messages.success(request, f"Subequipo '{subteam.name}' creado con éxito.")
            return redirect('manage_subteams')
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        # Inicializamos el formulario si es una solicitud GET
        subteam_form = SubTeamForm()

    return render(request, 'create_subteam.html', {
        'form': subteam_form,
        'available_athletes': available_athletes
    })  

#MANAGE SUBTEAM
@login_required
def manage_subteams(request):
    profile = request.user.profile
    if profile.is_coach():
        # Obtener los subequipos del coach y disponibles
        my_subteams = SubTeam.objects.filter(coaches=profile)
        available_subteams = SubTeam.objects.exclude(coaches=profile).filter(team=profile.olympic_team)

        return render(request, 'manage_subteams.html', {
            'my_subteams': my_subteams,
            'available_subteams': available_subteams,
        })
    return redirect('home')

# EDIT SUBTEAM
@login_required
def edit_subteam(request, subteam_id):
    subteam = get_object_or_404(SubTeam, id=subteam_id)
    profile = request.user.profile

    if not profile.is_coach():
        return redirect('home')

    # Verificar si el coach es el creador del subequipo
    is_creator = subteam.coaches.first() == profile

    # Manejar el cambio de nombre del subequipo
    if request.method == 'POST' and 'update_name' in request.POST:
        new_name = request.POST.get('name')
        if new_name:
            subteam.name = new_name
            subteam.save()
            messages.success(request, f"El nombre del subequipo se ha actualizado a '{new_name}'")
        else:
            messages.error(request, "El nombre del subequipo no puede estar vacío.")
        return redirect('edit_subteam', subteam_id=subteam.id)

    # Manejar la eliminación de un atleta del subequipo
    if request.method == 'POST' and 'remove_athlete' in request.POST:
        athlete_id = request.POST.get('athlete_id')
        athlete = Profile.objects.get(id=athlete_id)

        if is_creator and subteam.can_remove_athlete(athlete):
            subteam.athletes.remove(athlete)
            messages.success(request, f"{athlete.user.first_name} ha sido eliminado del subequipo.")
        else:
            messages.error(request, "No tienes permiso para eliminar a este atleta.")
        return redirect('edit_subteam', subteam_id=subteam.id)

    # Obtener los atletas actuales en el subequipo
    athletes_in_subteam = subteam.athletes.all()

    # Obtener los atletas disponibles que no estén ya en el subequipo
    available_athletes = Profile.objects.filter(
        olympic_team=subteam.team,
        role='Athlete'
    ).exclude(id__in=athletes_in_subteam)

    return render(request, 'edit_subteam.html', {
        'subteam': subteam,
        'athletes_in_subteam': athletes_in_subteam,
        'available_athletes': available_athletes,
        'is_creator': is_creator  # Pasamos si el coach es el creador
    })

# DELETE SUBTEAM
@login_required
def delete_subteam(request, subteam_id):
    subteam = get_object_or_404(SubTeam, id=subteam_id)

    if request.method == 'POST':
        subteam.delete()
        messages.success(request, f"El subequipo '{subteam.name}' ha sido eliminado.")
        return redirect('manage_subteams')

    return render(request, 'delete_subteam.html', {'subteam': subteam})

# JOIN SUBTEAM
@login_required
def join_subteam(request, subteam_id):
    subteam = get_object_or_404(SubTeam, id=subteam_id)
    profile = request.user.profile

    if subteam.coaches.count() >= 3:
        messages.error(request, "Este subequipo ya tiene el número máximo de 3 coaches.")
        return redirect('manage_subteams')

    subteam.coaches.add(profile)
    messages.success(request, 'Te has unido al subequipo exitosamente.')
    return redirect('manage_subteams')

# VIEW ATHLETE PROFILE
@login_required
def coach_view_athlete_profile(request, athlete_id):
    # Obtener el perfil del atleta por su ID
    athlete_profile = get_object_or_404(Profile, id=athlete_id, role='Athlete')
    full_name = f"{athlete_profile.user.first_name} {athlete_profile.user.last_name}"
    
    # Obtener las evaluaciones del atleta
    athlete_records = AthleteRecord.objects.filter(athlete=athlete_profile).order_by('-evaluation_date')
    
    # Verificar si el coach está en el mismo equipo olímpico y puede evaluar al atleta
    can_evaluate = athlete_profile.olympic_team == request.user.profile.olympic_team

    # Obtener el nombre del equipo olímpico
    team_name = athlete_profile.olympic_team.team_name if athlete_profile.olympic_team else 'No asignado'
    country = athlete_profile.olympic_country

    return render(request, 'coach_view_athlete_profile.html', {
        'profile': athlete_profile,
        'full_name': full_name,
        'athlete_records': athlete_records,
        'can_evaluate': can_evaluate,  # Usamos esta variable en el template para mostrar el botón
        'team_name': team_name,
        'country': country
    })

# ADD RECORD/EVALUATION
@login_required
def add_record(request):
    if request.method == 'POST':
        form = AthleteRecordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('coach_dashboard')  # O cualquier página que prefieras
    else:
        form = AthleteRecordForm()

    return render(request, 'add_record.html', {'form': form})

# EVALUATE ATHLETE
@login_required
def evaluate_athlete(request, athlete_id):
    athlete = get_object_or_404(Profile, id=athlete_id, role='Athlete')
    coach = request.user.profile
    full_name = f"{athlete.user.first_name} {athlete.user.last_name}"

    # Verificar si el coach está en el mismo equipo que el atleta
    if coach.is_coach() and athlete.olympic_team == coach.olympic_team:
        
        # Cargar los criterios de evaluación desde el archivo JSON
        criteria_file = settings.BASE_DIR / 'evaluation_criteria.json'
        with open(criteria_file, 'r', encoding='utf-8') as f:
            criteria_data = json.load(f)

        # Obtener los criterios para la disciplina y rama del atleta
        discipline = athlete.discipline
        branch = athlete.branch
        evaluation_criteria = criteria_data.get(discipline, {}).get(branch, [])
        evaluation_range = range(1, 11)  # Rango de puntuación

        # Siempre definimos el formulario, ya sea para GET o POST
        form = AthleteRecordForm(request.POST or None)

        if request.method == 'POST':
            if form.is_valid():
                # Guardamos el registro de evaluación general
                record = form.save(commit=False)
                record.athlete = athlete
                record.coach = coach
                record.save()

                # Guardar cada criterio evaluado
                for criterion in evaluation_criteria:
                    score = request.POST.get(f'criterion_{criterion}')
                    note = request.POST.get(f'note_{criterion}')

                    # Verificamos que haya una puntuación válida
                    if score:
                        EvaluationCriterion.objects.create(
                            athlete_record=record,
                            criterion_name=criterion,
                            score=int(score),
                            notes=note or ''
                        )

                messages.success(request, 'Evaluación guardada con éxito.')
                return redirect('coach_dashboard')
            else:
                # Si el formulario de evaluación no es válido
                print("Errores del formulario:", form.errors)
                messages.error(request, 'Error al guardar la evaluación. Revisa los campos obligatorios.')

        return render(request, 'evaluate_athlete.html', {
            'form': form,
            'athlete': athlete,
            'evaluation_criteria': evaluation_criteria,
            'evaluation_range': evaluation_range,
            'full_name': full_name,
        })
    else:
        messages.error(request, 'No tienes permiso para evaluar a este atleta.')
        return redirect('home')

# VIEW EVALUATION    
@login_required
def view_evaluation_detail(request, record_id):
    # Obtener el registro de la evaluación
    record = get_object_or_404(AthleteRecord, id=record_id)
    # Obtener los criterios asociados a esta evaluación
    evaluation_criteria = EvaluationCriterion.objects.filter(athlete_record=record)

    # Verificar si el usuario actual es el coach que hizo la evaluación
    can_edit = request.user.profile == record.coach

    return render(request, 'evaluation_detail.html', {
        'record': record,
        'evaluation_criteria': evaluation_criteria,
        'can_edit': can_edit
    })

# EDIT EVALUATION
@login_required
def edit_evaluation(request, record_id):
    record = get_object_or_404(AthleteRecord, id=record_id)
    if record.coach != request.user.profile:
        return redirect('home')  # Solo el coach autor puede editar

    if request.method == 'POST':
        form = AthleteRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Evaluación actualizada con éxito.")
            return redirect('view_evaluation_detail', record_id=record.id)
    else:
        form = AthleteRecordForm(instance=record)

    return render(request, 'edit_evaluation.html', {'form': form, 'record': record})

# DELETE EVALUATION
@login_required
def delete_evaluation(request, record_id):
    record = get_object_or_404(AthleteRecord, id=record_id)
    if record.coach != request.user.profile:
        return redirect('home')  # Solo el coach autor puede eliminar

    if request.method == 'POST':
        record.delete()
        messages.success(request, "Evaluación eliminada con éxito.")
        return redirect('coach_dashboard')

    return render(request, 'delete_evaluation.html', {'record': record})

####################################################################################################
#                                       ATHLETE                                                    #
####################################################################################################

# ATHLETE PROFILE
@login_required
def athlete_profile(request, athlete_id=None):
    if athlete_id:
        profile = get_object_or_404(Profile, id=athlete_id, role='Athlete')
    else:
        profile = request.user.profile

    full_name = f"{profile.user.first_name} {profile.user.last_name}"

    if profile.is_athlete() or request.user.profile.is_coach():
        latest_record = AthleteRecord.objects.filter(athlete=profile).order_by('-evaluation_date').first()

        # Obtener el coach del atleta si está asignado
        coach = Profile.objects.filter(
            role='Coach',
            discipline=profile.discipline,
            branch=profile.branch
        ).first()

        # Acceder al nombre del equipo olímpico a través del coach
        team_name = coach.olympic_team.team_name if coach and coach.olympic_team else 'No asignado'

        # Mejores atletas
        best_athletes = Profile.objects.filter(
            discipline=profile.discipline,
            branch=profile.branch,
            role='Athlete'
        ).annotate(
            max_score=Max(F('athlete_records__difficulty') + F('athlete_records__execution'))
        ).order_by('-max_score')[:5]

        # Campeones de las Olimpiadas
        champions = {
            'Uneven Bars': {'name': 'Rebeca Andrade', 'country': 'Brasil', 'difficulty': 6, 'execution': 8, 'score': 14},
            'Floor': {'name': 'Ana Barbosu', 'country': 'Rumania', 'difficulty': 5, 'execution': 7, 'score': 12},
            'Balance Beam': {'name': 'Luisa Blanco', 'country': 'Colombia', 'difficulty': 5, 'execution': 7, 'score': 12},
        }
        champion = champions.get(profile.branch, None)

        olympic_country = profile.olympic_country
        athlete_records = AthleteRecord.objects.filter(athlete=profile)

        # Permisos de edición de registros
        can_edit_records = request.user.profile.is_coach() and athlete_records.filter(coach=request.user.profile).exists()

        # Formulario de cambio de contraseña
        if request.user == profile.user:
            if request.method == 'POST':
                form = PasswordChangeForm(user=request.user, data=request.POST)
                if form.is_valid():
                    user = form.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
                    return redirect('athlete_profile', athlete_id=profile.id)
            else:
                form = PasswordChangeForm(user=request.user)
        else:
            form = None

        return render(request, 'athlete_profile.html', {
            'profile': profile,
            'full_name': full_name,
            'latest_record': latest_record,
            'best_athletes': best_athletes,
            'champion': champion,
            'team_name': team_name,
            'olympic_country': olympic_country,
            'athlete_records': athlete_records,
            'can_edit_records': can_edit_records,
            'form': form
        })

    return redirect('home')

# ATHLETE RECORDS
@login_required
def view_athlete_records(request, athlete_id):
    athlete = get_object_or_404(Profile, id=athlete_id, role='Athlete')
    full_name = f"{athlete.user.first_name} {athlete.user.last_name}"
    records = AthleteRecord.objects.filter(athlete=athlete)
    return render(request, 'view_records.html', {'athlete': athlete, 'full_name': full_name, 'records': records})

# COMPARISON OPTIONS (ONLY OPTIONS)
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

# COMPARE PERSONAL RECORDS
@login_required
def compare_personal_records(request):
    profile = request.user.profile

    # Limpiar mensajes pendientes para evitar que se arrastren
    storage = messages.get_messages(request)
    for _ in storage:
        pass  # Elimina los mensajes pendientes

    if profile.is_athlete():
        personal_records = AthleteRecord.objects.filter(athlete=profile).order_by('-evaluation_date')

        if request.method == 'POST':
            record_1_id = request.POST.get('record_1')
            record_2_id = request.POST.get('record_2')

            if not record_1_id or not record_2_id:
                messages.set_level(request, messages.ERROR)
                messages.error(request, 'Por favor selecciona dos récords diferentes para comparar.')
                return render(request, 'compare_personal_records.html', {'records': personal_records})

            if record_1_id == record_2_id:
                messages.set_level(request, messages.ERROR)
                messages.error(request, 'No puedes comparar el mismo récord.')
                return render(request, 'compare_personal_records.html', {'records': personal_records})

            record_1 = get_object_or_404(AthleteRecord, id=record_1_id)
            record_2 = get_object_or_404(AthleteRecord, id=record_2_id)

            # Calcular la diferencia de puntuación
            score_difference = record_1.total_score() - record_2.total_score()
            abs_difference = abs(score_difference)

            return render(request, 'compare_personal_records_result.html', {
                'record_1': record_1,
                'record_2': record_2,
                'score_difference': score_difference,
                'abs_difference': abs_difference,  # Añadimos la diferencia para usar en el template
            })

        return render(request, 'compare_personal_records.html', {'records': personal_records})
    return redirect('home')

# COMPARE WITH OTHER ATHLETES
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
            abs_difference = abs(score_difference)

            return render(request, 'compare_with_athletes_result.html', {
                'athlete': profile,
                'athlete_record': current_athlete_record,
                'compare_athlete': selected_athlete,
                'compare_record': selected_athlete_record,
                'score_difference': score_difference,
                'abs_difference': abs_difference
            })

        return render(request, 'compare_with_athletes.html', {'athletes': other_athletes})
    return redirect('home')