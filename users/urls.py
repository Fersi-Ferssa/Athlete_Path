from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (view_evaluation_detail, edit_evaluation, delete_evaluation)

urlpatterns = [
    path('home/', views.home, name='home'),
    path('view_team/', views.view_team, name='view_team'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_change_form.html'), name='password_change'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    path('password_reset/', views.password_reset_view, name='password_reset'),  # Línea corregida
    path('register/', views.register, name='register'),
    path('dashboard/coach/', views.coach_dashboard, name='coach_dashboard'),
    path('add_record/', views.add_record, name='add_record'),
    path('evaluate/athlete/<int:athlete_id>/', views.evaluate_athlete, name='evaluate_athlete'),
    path('comparison_options/', views.comparison_options, name='comparison_options'),
    path('compare_personal_records/', views.compare_personal_records, name='compare_personal_records'),
    path('compare_with_athletes/', views.compare_with_athletes, name='compare_with_athletes'),
    path('get_branches/', views.get_branches, name='get_branches'),
    path('manage_subteams/', views.manage_subteams, name='manage_subteams'),
    path('create_subteam/', views.create_subteam, name='create_subteam'),
    path('edit_subteam/<int:subteam_id>/', views.edit_subteam, name='edit_subteam'),
    path('delete_subteam/<int:subteam_id>/', views.delete_subteam, name='delete_subteam'),
    path('join_subteam/<int:subteam_id>/', views.join_subteam, name='join_subteam'),
    path('profile/', views.coach_profile, name='profile'),
    path('profile/athlete/', views.athlete_profile, name='athlete_profile'),
    path('coach/view_athlete_profile/<int:athlete_id>/', views.coach_view_athlete_profile, name='coach_view_athlete_profile'),
    path('evaluation/<int:record_id>/', views.view_evaluation_detail, name='view_evaluation_detail'),
    path('evaluation/edit/<int:record_id>/', views.edit_evaluation, name='edit_evaluation'),
    path('evaluation/delete/<int:record_id>/', views.delete_evaluation, name='delete_evaluation'),
    path('request_team_unsubscribe/', views.request_team_unsubscribe, name='request_team_unsubscribe'),
    path('athlete_records/<int:athlete_id>/', views.view_athlete_records, name='view_athlete_records'),
    path('athlete/evaluation/<int:record_id>/', views.athlete_view_evaluation_detail, name='athlete_view_evaluation_detail'),
]