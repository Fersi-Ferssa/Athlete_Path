from django.shortcuts import render
from django.contrib.auth.decorators import login_required  # Decorador para restringir el acceso a usuarios autenticados

@login_required  # Requiere que el usuario esté autenticado para acceder a esta vista
def home(request):
    # Renderiza la plantilla 'home.html' y pasa el contexto al usuario que ha iniciado sesión
    return render(request, 'home.html')