from django.shortcuts import render
from django.contrib.auth.decorators import login_required  # Decorador para restringir el acceso a usuarios autenticados

def home(request):
    return render(request, 'home.html')  # El template 'home.html' debe estar en la carpeta 'templates'
