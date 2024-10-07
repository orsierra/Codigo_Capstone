from django.shortcuts import render, redirect
from .models import Alumno
from .forms import AlumnoForm

#Páginas
def home(request):
    return render(request, 'core/home.html')

def login_view(request):
    return render(request, 'login.html')

#DIRECTOR

def director_view(request):
    return render(request, 'director.html')

def directorFinanzas_view(request):
    return render(request, 'directorFinanzas.html')

def directorInforme_view(request):
    return render(request, 'directorInforme.html') 

def directorMenu_view(request):
    return render(request, 'directorMenu.html')

def directorPlanificacion_view(request):
    return render(request, 'directorPlanificacion.html')

#ESTUDIANTE


def estudiante_view(request):
    return render(request, 'estudiante.html')

def sostenedor_view(request):
    return render(request, 'sostenedor.html')

def estudiante_pru_base(request):
    return render(request, 'estudiante_pru_base.html')

#APODERADO

def apoderado_view(request):
    return render(request, 'apoderado.html')

def apoderadoAsistencia_view(request):
    return render(request, 'apoderadoAsistencia.html')

def apoderadoMatricula_view(request):
    return render(request, 'apoderadoMatricula.html')

#PROFESOR

def profesor_asistencia_view(request):
    # Lógica para mostrar el formulario de agregar alumnos y la tabla de asistencia
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('profesor_asistencia')  # Cambia a tu URL correspondiente
    else:
        form = AlumnoForm()

    alumnos = Alumno.objects.all()
    return render(request, 'profesorAsistencia.html', {'form': form, 'alumnos': alumnos})

def registrar_asistencia_view(request, curso_id):
    # Aquí puedes agregar la lógica para registrar la asistencia de los alumnos de un curso específico.
    # Puedes usar el curso_id para filtrar los alumnos.
    if request.method == 'POST':
        # Lógica para guardar la asistencia
        pass  # Implementa la lógica aquí

    # Filtra los alumnos del curso
    alumnos = Alumno.objects.filter(curso_id=curso_id)
    return render(request, 'registrar_asistencia.html', {'alumnos': alumnos})