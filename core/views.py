# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Curso,Profesor
from django.contrib.auth.models import User


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profesor')  # Redirige a la página principal del rol correspondiente
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')
# Esta vista está protegida, solo accesible si el usuario ha iniciado sesión
@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

# views.py


@login_required
def profesor_dashboard(request):
    return render(request, 'profesor.html')  # Renderiza el dashboard del profesor
# views.py
@login_required
def profesor_cursos(request):
    cursos = Curso.objects.filter(profesor=request.user.profesor)  # Asumiendo que has relacionado el usuario con el profesor
    return render(request, 'profesorCursos.html', {'cursos': cursos})

def crear_usuario_db(request):
    # Crear un usuario si no existe
    user = User.objects.create_user(username='Orly', password='contraseña', email='orlandone@gmail.com')

# Crear un profesor
    profesor = Profesor.objects.create(user=user, nombre='Orly', apellido='Tapia', email='orlandone@gmail.com')
    return redirect(login)



