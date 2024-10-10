from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from .models import Curso, Estudiante, Asistencia, Profesor
from .forms import AsistenciaForm
from .models import Profesor 
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

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
class AsistenciaCursoView(View):
    def get(self, request, curso_id):
        curso = get_object_or_404(Curso, id=curso_id)
        estudiantes = curso.estudiantes.all()
        asistencia_forms = [AsistenciaForm(initial={'estudiante': estudiante, 'curso': curso}) for estudiante in estudiantes]
        return render(request, 'asistencia_curso.html', {'curso': curso, 'asistencia_forms': asistencia_forms})

    def post(self, request, curso_id):
        curso = get_object_or_404(Curso, id=curso_id)
        for form in request.POST.getlist('form'):
            form_data = {**request.POST, **form}
            asistencia_form = AsistenciaForm(data=form_data)
            if asistencia_form.is_valid():
                asistencia_form.save()
        return redirect('asistencia_curso', curso_id=curso_id)

#PROFESOR


from .models import Curso, Asistencia
class AsistenciaCursoView(View):
    def get(self, request, curso_id):
        curso = get_object_or_404(Curso, id=curso_id)
        asistencia = Asistencia.objects.filter(curso=curso)
        return render(request, 'asistencia_curso.html', {'curso': curso, 'asistencia': asistencia})

def profesorCalificacion_view(request):
    return render(request, 'profesorCalificacion.html')

def profesorMisCursos_view(request):
    return render(request, 'profesorMisCursos.html')

def profesorObservacion_view(request):
    return render(request, 'profesorObservacion.html')

from django.shortcuts import render, get_object_or_404, redirect
from .models import Evaluacion, Profesor, Estudiante, Asignatura
from .forms import EvaluacionForm
from django.contrib.auth.decorators import login_required

@login_required
def lista_estudiantes_profesor(request):
    profesor = get_object_or_404(Profesor, correo=request.user.email)  # Asumimos que el profesor usa su correo para autenticarse
    asignaturas = Asignatura.objects.filter(profesor_id_profesor=profesor.id_profesor)  # Obtener asignaturas del profesor

    # Lista de estudiantes en base a las asignaturas del profesor
    estudiantes = Estudiante.objects.filter(curso__asignatura__in=asignaturas)

    return render(request, 'profesor/lista_estudiantes.html', {
        'estudiantes': estudiantes,
        'asignaturas': asignaturas
    })
    
from django.shortcuts import render
from .models import Estudiante  # Asegúrate de tener el modelo adecuado

def agregar_nota(request):
    estudiantes = Estudiante.objects.all()  # Obtenemos todos los estudiantes

    if request.method == 'POST':
        # Procesamos el envío del formulario
        for estudiante in estudiantes:
            nota = request.POST.get(f'nota_{estudiante.id}')
            estudiante.nota = nota
            estudiante.save()
        return redirect('lista_estudiantes_profesor')  # Redirigir después de guardar

    return render(request, 'calificaciones/profesorCalificacion.html', {'estudiantes': estudiantes})


#DIRECTOR

def planificacion_academica(request):
    profesores = Profesor.objects.all()  # Obtén todos los profesores desde la base de datos
    return render(request, 'directorPlanificacion.html', {'profesores': profesores})


# Imprimir PDF

def imprimir_pdf(request):
    profesores = Profesor.objects.all()  # Obtener todos los profesores
    html_string = render_to_string('planificacion_pdf.html', {'profesores': profesores})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="planificacion_academica.pdf"'
    HTML(string=html_string).write_pdf(response)
    return response