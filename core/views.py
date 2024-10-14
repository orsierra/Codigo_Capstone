# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Curso, Profesor,Asistencia, Calificacion, RegistroAcademico, Informe, Observacion, Alumno
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from datetime import date
from django.utils import timezone
from .forms import CalificacionForm


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

def libro_clases(request, curso_id):
    # Obtener el curso específico con el ID proporcionado
    curso = get_object_or_404(Curso, id=curso_id)
    
    # Pasar los datos del curso a la plantilla
    context = {
        'curso': curso,
    }

    # Renderizar la plantilla 'profesorLibro.html'
    return render(request, 'profesorLibro.html', context)
# VISTAS DE PROFESOR MIS CURSOS

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Curso, Asistencia, Alumno  # Asegúrate de importar tus modelos

@login_required
def registrar_asistencia(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    alumnos = curso.alumnos.all()  # Obtener los alumnos del curso

    if request.method == 'POST':
        # Crear o obtener la asistencia para la fecha actual
        asistencia, created = Asistencia.objects.get_or_create(curso=curso, fecha=timezone.now().date())

        # Limpiar las listas existentes para evitar duplicados
        asistencia.alumnos_presentes.clear()
        asistencia.alumnos_ausentes.clear()
        asistencia.alumnos_justificados.clear()

        # Procesar los estados de asistencia
        for alumno in alumnos:
            asistencia_value = request.POST.get(f'asistencia_{alumno.id}')
            if asistencia_value == 'presente':
                asistencia.alumnos_presentes.add(alumno)
            elif asistencia_value == 'ausente':
                asistencia.alumnos_ausentes.add(alumno)
            elif asistencia_value == 'justificado':
                asistencia.alumnos_justificados.add(alumno)
        
        asistencia.save()
        return redirect('profesor_cursos')  # Redirigir a la lista de cursos
    

    return render(request, 'registrarAsistencia.html', {'curso': curso, 'alumnos': alumnos})

#=============================================================== REGISTRAR CALIFICACIONES ====================================================================

from django.contrib import messages

def registrar_calificaciones(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    errores = {}
    form_list = {}

    if request.method == 'POST':
        for alumno in Alumno.objects.filter(curso=curso):
            form = CalificacionForm(request.POST, prefix=str(alumno.id))
            if form.is_valid():
                # Guarda la calificación usando el alumno y curso correcto
                calificacion = form.save(commit=False)  # No guarda aún en la base de datos
                calificacion.alumno = alumno  # Asocia el alumno
                calificacion.curso = curso  # Asocia el curso
                calificacion.save()  # Guarda en la base de datos
            else:
                errores[alumno] = form.errors  # Guarda los errores

        if not errores:
            messages.success(request, "Se han guardado los cambios exitosamente.")
            return redirect('registrar_calificaciones', curso_id=curso.id)

    else:
        # Crea formularios para cada alumno
        form_list = {alumno: CalificacionForm(prefix=str(alumno.id)) for alumno in Alumno.objects.filter(curso=curso)}

    return render(request, 'registrarCalificaciones.html', {
        'curso': curso,
        'form_list': form_list,
        'errores': errores
    })


#=============================================================================================================================================================

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


