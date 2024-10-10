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


# views.py

from django.shortcuts import render
from .models import Estudiante, Observacion

def observaciones_view(request):
    if request.method == 'POST':
        # Recoger los datos enviados desde el formulario
        observaciones = request.POST.getlist('observacion')
        estudiantes = request.POST.getlist('estudiante')

        # Guardar las observaciones
        for i, estudiante_id in enumerate(estudiantes):
            if observaciones[i]:
                # Guardar la observación en la base de datos
                observacion = Observacion(
                    estudiante_id_estudiante_id=estudiante_id,
                    observacion=observaciones[i]
                )
                observacion.save()

        # Mensaje de éxito
        return render(request, 'profesorObservacion.html', {'success': True})

    # Obtener estudiantes y concatenar nombre y apellido
    estudiantes = Estudiante.objects.all()

    return render(request, 'profesorObservacion.html', {
        'estudiantes': estudiantes
    })
# views.py
from django.shortcuts import render
from .models import Estudiante, Evaluacion, Asistencia

def registro_academico(request, estudiante_id):
    estudiante = Estudiante.objects.get(id=estudiante_id)
    evaluaciones = Evaluacion.objects.filter(estudiante=estudiante)
    asistencias = Asistencia.objects.filter(estudiante=estudiante)

    return render(request, 'registro_academico.html', {
        'estudiante': estudiante,
        'evaluaciones': evaluaciones,
        'asistencias': asistencias,
    })
# informes/views.py
from django.shortcuts import render, get_object_or_404
from .models import Alumno, Curso
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template

def generar_informe(request, curso_id):
    # Obtener el curso basado en el id
    curso = get_object_or_404(Curso, id=curso_id)
    # Obtener todos los alumnos de ese curso
    alumnos = curso.alumnos.all()
    return render(request, 'informes/generar_informe.html', {'alumnos': alumnos, 'curso': curso})

# informes/views.py
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import Curso, Alumno
from xhtml2pdf import pisa
from django.template.loader import get_template

def generar_informe(request, curso_id):
    # Obtener el curso y los alumnos
    curso = get_object_or_404(Curso, id=curso_id)
    alumnos = Alumno.objects.filter(curso=curso)

    # Para generar el PDF
    if request.GET.get('pdf'):
        return generar_pdf_informe(curso, alumnos)

    # Renderizar la página de informe
    context = {
        'curso': curso,
        'alumnos': alumnos,
    }
    return render(request, 'informes/generar_informe.html', context)


def generar_pdf_informe(curso, alumnos):
    # Puedes calcular el promedio y la asistencia si tienes esos datos en tu modelo.
    promedio = sum(alumno.nota for alumno in alumnos) / len(alumnos) if alumnos else 0
    total_asistencia = sum(alumno.asistencia for alumno in alumnos)  # Ajusta el campo si es necesario.

    context = {
        'curso': curso,
        'alumnos': alumnos,
        'promedio': promedio,
        'total_asistencia': total_asistencia,
    }

    # Renderizar el template PDF
    template = get_template('informes/pdf_template.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="informe_curso_{curso.id}.pdf"'

    # Crear el PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error al generar el PDF')
    return response
#SOSTENEDOR
from django.shortcuts import render, redirect, get_object_or_404
from .models import Establecimiento
from .forms import EstablecimientoForm

def sostenedor_menu(request, id=None):
    establecimientos = Establecimiento.objects.all()  # Todos los establecimientos

    if id:
        # Si hay un ID, entonces es una edición
        establecimiento = get_object_or_404(Establecimiento, id=id)
    else:
        # Si no hay ID, estamos creando un nuevo establecimiento
        establecimiento = None

    if request.method == 'POST':
        form = EstablecimientoForm(request.POST, instance=establecimiento)
        if form.is_valid():
            form.save()
            return redirect('sostenedor_menu')  # Redirigir después de guardar
    else:
        form = EstablecimientoForm(instance=establecimiento)

    # Renderizar el HTML con los datos de los establecimientos y el formulario
    return render(request, 'sostenedorMenu.html', {
        'establecimientos': establecimientos,
        'form': form,
        'edit_mode': bool(id),  # True si es edición
        'edit_id': id  # El ID del establecimiento que estamos editando (si es edición)
    })
    from django.shortcuts import render
from .models import Curso

def consulta_informes(request):
    # Obtener todos los cursos para mostrarlos
    cursos = Curso.objects.all()  # Aquí puedes filtrar según los requisitos
    return render(request, 'subdireConsu.html', {'cursos': cursos})






