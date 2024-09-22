from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('dashboard/coach/', views.coach_dashboard, name='coach_dashboard'),
    path('profile/athlete/', views.athlete_profile, name='athlete_profile'),
    path('add_record/', views.add_record, name='add_record'),
    path('evaluate/athlete/<int:athlete_id>/', views.evaluate_athlete, name='evaluate_athlete'),
]