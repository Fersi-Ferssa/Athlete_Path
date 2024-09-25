from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_change_form.html'), name='password_change'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    path('password_reset/', views.password_reset_view, name='password_reset'),  # Línea corregida
    path('register/', views.register, name='register'),
    path('dashboard/coach/', views.coach_dashboard, name='coach_dashboard'),
    path('profile/athlete/', views.athlete_profile, name='athlete_profile'),
    path('add_record/', views.add_record, name='add_record'),
    path('evaluate/athlete/<int:athlete_id>/', views.evaluate_athlete, name='evaluate_athlete'),
    path('comparison_options/', views.comparison_options, name='comparison_options'),
    path('compare_personal_records/', views.compare_personal_records, name='compare_personal_records'),
    path('compare_with_athletes/', views.compare_with_athletes, name='compare_with_athletes'),
]