# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Curso, Profesor
from django.contrib.auth.models import User

from .models import Asistencia, Calificacion, RegistroAcademico, Informe, Observacion
from django.shortcuts import render, get_object_or_404

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
    profesor = Profesor.objects.get(user=request.user)  # Obtener el profesor basado en el usuario logueado
    cursos = Curso.objects.filter(profesor=profesor)  # Obtener los cursos asociados a ese profesor
    context = {
        'profesor': profesor,
        'cursos': cursos,
    }
    return render(request, 'profesorCursos.html', context)

def crear_usuario_db(request):
    # Crear un usuario si no existe
    user = User.objects.create_user(username='Orly', password='contraseña', email='orlandone@gmail.com')

# Crear un profesor
    profesor = Profesor.objects.create(user=user, nombre='Orly', apellido='Tapia', email='orlandone@gmail.com')
    return redirect(login)

# VIEWS PROFESOR LIBRO

def profesor_libro(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    return render(request, 'profesorLibro.html', {'curso': curso})
# VISTAS DE PROFESOR MIS CURSOS

@login_required
def registrar_asistencia(request, curso_id):
    curso = Curso.objects.get(id=curso_id)
    if request.method == "POST":
        # Lógica para registrar asistencia
        pass
    return render(request, 'registrar_asistencia.html', {'curso': curso})

@login_required
def registrar_calificaciones(request, curso_id):
    curso = Curso.objects.get(id=curso_id)
    if request.method == "POST":
        # Lógica para registrar calificaciones
        pass
    return render(request, 'registrar_calificaciones.html', {'curso': curso})

@login_required
def registro_academico(request, curso_id):
    curso = Curso.objects.get(id=curso_id)
    registros = RegistroAcademico.objects.filter(curso=curso)
    return render(request, 'registro_academico.html', {'curso': curso, 'registros': registros})

@login_required
def generar_informes(request, curso_id):
    curso = Curso.objects.get(id=curso_id)
    informes = Informe.objects.filter(curso=curso)
    return render(request, 'generar_informes.html', {'curso': curso, 'informes': informes})

@login_required
def observaciones(request, curso_id):
    curso = Curso.objects.get(id=curso_id)
    observaciones = Observacion.objects.filter(curso=curso)
    return render(request, 'observaciones.html', {'curso': curso, 'observaciones': observaciones})

#====================================================================================================================================================


