from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('add_record/', views.add_record, name='add_record'),
    path('records/<int:athlete_id>/', views.view_athlete_records, name='view_records'),
]