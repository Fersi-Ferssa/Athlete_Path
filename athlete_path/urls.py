"""
URL configuration for athlete_path project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# Lista de patrones URL que asignan rutas a vistas y otros archivos URL
urlpatterns = [
    # URL para la administración de Django
    path('admin/', admin.site.urls),
    
    # Incluir URLs relacionadas con autenticación (login, logout, etc.) que Django maneja por defecto
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Incluir las URLs definidas en la aplicación 'users' (por ejemplo, para registro, login, home, etc.)
    path('users/', include('users.urls')),
]