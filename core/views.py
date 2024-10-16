# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Curso, Profesor,Asistencia, Calificacion, Informe, Observacion, Alumno, Apoderado
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from datetime import date
from django.utils import timezone
from .forms import CalificacionForm, ObservacionForm 
from django.contrib import messages
from django.db.models import Avg
from django.http import HttpResponse
import io
from io import BytesIO
from collections import defaultdict
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph,  Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
import json
import logging
from django.http import JsonResponse
from django.db.models import Q  # Agrega esta línea

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redireccionar según el rol del usuario
            if hasattr(user, 'alumno'):  # Verifica si el usuario tiene un perfil de alumno
                return redirect('alumno_home')  # Redirigir al alumno
            elif hasattr(user, 'profesor'):  # Verifica si el usuario tiene un perfil de profesor
                return redirect('profesor')  # Redirigir al profesor
            elif hasattr(user, 'apoderado'):  # Verifica si el usuario tiene un perfil de apoderado
                return redirect('apoderado_view')  # Redirigir al apoderado
            else:
                return redirect('default')  # Redirigir a una página predeterminada
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'login.html')

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

# ======================================================= VIEWS PROFESOR LIBRO =============================================================================

def libro_clases(request, curso_id):
    # Obtener el curso específico con el ID proporcionado
    curso = get_object_or_404(Curso, id=curso_id)
    
    # Pasar los datos del curso a la plantilla
    context = {
        'curso': curso,
    }

    # Renderizar la plantilla 'profesorLibro.html'
    return render(request, 'profesorLibro.html', context)
# ==========================================================================================================================================================

# ================================================================= REGISTRAR ASISTENCIA ==================================================================

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
        messages.success(request, "Los cambios se han guardado exitosamente.")
        return redirect('registrar_asistencia', curso_id=curso.id)  # Cambia aquí a la vista de registrar asistencia

    return render(request, 'registrarAsistencia.html', {'curso': curso, 'alumnos': alumnos})



#=============================================================== REGISTRAR CALIFICACIONES ====================================================================

@login_required
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
            return redirect('registrar_calificaciones', curso_id=curso_id)  # Cambia aquí

    else:
        # Crea formularios para cada alumno
        form_list = {alumno: CalificacionForm(prefix=str(alumno.id)) for alumno in Alumno.objects.filter(curso=curso)}

    return render(request, 'registrarCalificaciones.html', {
        'curso': curso,
        'form_list': form_list,
        'errores': errores
    })


# =================================================== REGISTRO ACADEMICO =====================================================================================

@login_required
def registro_academico(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    alumnos = curso.alumnos.all()
    calificaciones = Calificacion.objects.filter(curso=curso)
    asistencias = Asistencia.objects.filter(curso=curso)

    # Construir un diccionario para mapear alumnos a sus calificaciones
    calificaciones_por_alumno = {}
    promedios_por_alumno = {}
    asistencias_por_alumno = {}

    for alumno in alumnos:
        calificaciones_alumno = calificaciones.filter(alumno=alumno)
        calificaciones_por_alumno[alumno] = calificaciones_alumno

        # Calcular el promedio de calificaciones
        promedio = calificaciones_alumno.aggregate(Avg('nota'))['nota__avg'] or 0
        promedios_por_alumno[alumno] = promedio

        # Obtener asistencias para cada alumno
        asistencias_alumno = asistencias.filter(alumnos_presentes=alumno) | asistencias.filter(alumnos_ausentes=alumno)
        asistencias_por_alumno[alumno] = asistencias_alumno

    context = {
        'curso': curso,
        'calificaciones_por_alumno': calificaciones_por_alumno,
        'promedios_por_alumno': promedios_por_alumno,
        'asistencias_por_alumno': asistencias_por_alumno,
    }
    return render(request, 'registroAcademico.html', context)
# ===============================================================================================================================================================

@login_required
def generar_informes(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    alumnos = Alumno.objects.filter(curso=curso)  # Obtener los alumnos del curso
    return render(request, 'Profe_generar_informes.html', {'curso': curso, 'alumnos': alumnos})

def generar_pdf(request):
    if request.method == 'POST':
        try:
            # Obtener los datos de la solicitud
            data = json.loads(request.body)
            alumno_id = int(data.get('alumno_id', 0))
            curso_id = int(data.get('curso_id', 0))

            # Validación de datos
            if not alumno_id or not curso_id:
                return JsonResponse({'error': 'Los campos alumno_id y curso_id son requeridos'}, status=400)

            # Obtener los datos del alumno, curso, calificaciones y asistencias
            alumno = Alumno.objects.get(id=alumno_id)
            curso = Curso.objects.get(id=curso_id)
            calificaciones = Calificacion.objects.filter(alumno=alumno, curso=curso)
            asistencias = Asistencia.objects.filter(alumno=alumno, curso=curso)

            # Crear el PDF utilizando ReportLab
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            story = []

            # Agregar encabezado con estilo
            styles = getSampleStyleSheet()
            styleH1 = styles["Heading1"]
            story.append(Paragraph(f"Informe de {alumno.nombre} {alumno.apellido} - {curso.nombre}", styleH1))

            # Crear tabla de calificaciones y asistencias
            data = [
                ['Asignatura', 'Nota', 'Asistencia (%)']
            ]
            for calificacion in calificaciones:
                total_asistencias_alumno = asistencias.filter(alumno=calificacion.alumno).count()
                total_clases_posibles = Curso.objects.get(id=curso_id).total_clases
                asistencia_porcentaje = (total_asistencias_alumno / total_clases_posibles) * 100
                data.append([calificacion.asignatura.nombre, calificacion.nota, f"{asistencia_porcentaje:.2f}%"])

            # Crear tabla con estilo
            table = Table(data)
            table.setStyle(TableStyle([
                ('ALIGN', (1,1), (-2,-2), 'RIGHT'),
                ('TEXTCOLOR', (1,1), (-2,-2), colors.blue),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            story.append(table)

            # Generar el PDF
            doc.build(story)

            # Enviar el PDF como respuesta
            buffer.seek(0)
            return HttpResponse(buffer.getvalue(), content_type='application/pdf')

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Solo se permiten solicitudes POST'}, status=405)


# =============================================================== OBSERVACIONES =========================================================================

@login_required
def observaciones(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    observaciones = Observacion.objects.filter(curso=curso)

    if request.method == 'POST':
        form = ObservacionForm(request.POST)
        if form.is_valid():
            observacion = form.save(commit=False)
            observacion.curso = curso  # Asociar la observación al curso
            # Aquí no necesitas asignar el alumno, ya que el formulario tendrá el campo de selección
            observacion.save()
            return redirect('observaciones', curso_id=curso.id)  # Redirigir después de guardar
    else:
        # Al crear el formulario, solo incluir alumnos del curso actual
        form = ObservacionForm()
        form.fields['alumno'].queryset = curso.alumnos.all()  # Filtrar alumnos

    return render(request, 'observaciones.html', {
        'curso': curso,
        'observaciones': observaciones,
        'form': form,
    })

#========================================================================================================================================================
#alumno consulta asitencia y notas
# Vista para el panel del alumno
def alumno_dashboard(request):
    return render(request, 'alumno.html')

# Vista para la consulta de asistencia
@login_required
def alumno_consulta_asistencia(request):
    alumno = get_object_or_404(Alumno, user=request.user)
    cursos = Curso.objects.filter(alumnos=alumno)  # Obtener los cursos del alumno
    asistencias_data = []

    # Recorremos los cursos del alumno para obtener la información de asistencia
    for curso in cursos:
        total_clases = Asistencia.objects.filter(curso=curso).count()  # Total de clases (días)
        asistencias_presente = Asistencia.objects.filter(curso=curso, alumnos_presentes=alumno).count()  # Total de asistencias
        asistencias_justificado = Asistencia.objects.filter(curso=curso, alumnos_justificados=alumno).count()  # Total de justificados

        # Se suma el presente con el justificado para obtener el total de asistencia válida
        total_asistencia = asistencias_presente + asistencias_justificado
        porcentaje_asistencia = (total_asistencia / total_clases * 100) if total_clases > 0 else 0

        asistencias_data.append({
            'curso': curso.nombre,
            'asignatura': curso.asignatura,
            'total_clases': total_clases,
            'asistencia': total_asistencia,
            'porcentaje_asistencia': round(porcentaje_asistencia, 2)
        })

    return render(request, 'alumnoConsuAsis.html', {'asistencias_data': asistencias_data})

# Vista para la consulta de notas
def alumno_consulta_notas(request):
    return render(request, 'alumnoConsuNotas.html')
#alumno home
@login_required
def alumno_home(request):
    # Aquí puedes obtener más información del alumno si es necesario
    alumno = request.user.alumno  # Si tienes un modelo 'Alumno' relacionado con 'User'
    
    context = {
        'alumno': alumno
    }
    return render(request, 'alumno.html', context)

# views.py APODERADO
def apoderado_view(request):
    # Aquí podrías agregar lógica para obtener datos relevantes para el apoderado si es necesario
    return render(request, 'apoderado.html')

@login_required
def apoderadoConsuAsis(request):
    apoderado = get_object_or_404(Apoderado, user=request.user)
    alumnos = Alumno.objects.filter(apoderado=apoderado)  # Obtener los alumnos del apoderado
    asistencias_data = []

    # Recorremos los alumnos para obtener la información de asistencia
    for alumno in alumnos:
        cursos = Curso.objects.filter(alumnos=alumno)  # Obtener los cursos del alumno
        
        for curso in cursos:
            total_clases = Asistencia.objects.filter(curso=curso).count()  # Total de clases (días)
            asistencias_presente = Asistencia.objects.filter(curso=curso, alumnos_presentes=alumno).count()  # Total de asistencias
            asistencias_justificado = Asistencia.objects.filter(curso=curso, alumnos_justificados=alumno).count()  # Total de justificados

            # Se suma el presente con el justificado para obtener el total de asistencia válida
            total_asistencia = asistencias_presente + asistencias_justificado
            porcentaje_asistencia = (total_asistencia / total_clases * 100) if total_clases > 0 else 0

            asistencias_data.append({
                'nombre_alumno': alumno.nombre,  # Asegúrate de que el modelo Alumno tenga este campo
                'curso': curso.nombre,
                'asignatura': curso.asignatura,
                'total_clases': total_clases,
                'asistencia': total_asistencia,
                'porcentaje_asistencia': round(porcentaje_asistencia, 2)
            })

    return render(request, 'apoderadoConsuAsis.html', {'asistencias_data': asistencias_data})



def apoderadoConsuNotas(request):
    try:
        apoderado = Apoderado.objects.get(user=request.user)
    except Apoderado.DoesNotExist:
        return render(request, 'error.html', {'mensaje': 'No se encontró apoderado para este usuario.'})

    try:
        alumno = Alumno.objects.get(apoderado=apoderado)
    except Alumno.DoesNotExist:
        return render(request, 'error.html', {'mensaje': 'No se encontró un alumno asociado con este apoderado.'})

    calificaciones = Calificacion.objects.filter(alumno=alumno)
    cursos = Curso.objects.filter(calificacion__alumno=alumno).distinct()

    # Calcular el promedio de cada curso
    for curso in cursos:
        calificaciones_curso = calificaciones.filter(curso=curso)
        total_notas = sum(c.nota for c in calificaciones_curso if c.nota is not None)
        count_notas = calificaciones_curso.count()
        curso.promedio = total_notas / count_notas if count_notas > 0 else 0

    context = {
        'calificaciones': calificaciones,
        'cursos': cursos,
        'alumno': alumno
    }
    return render(request, 'apoderadoConsuNotas.html', context)


def apoderadoMatri(request):
    return render(request, 'apoderadoMatri.html')

