# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Curso, Profesor,Asistencia, Calificacion, Informe, Observacion, Alumno, Apoderado, Curso
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from datetime import date
from django.utils import timezone
from .forms import CalificacionForm, ObservacionForm, AlumnoForm, ApoderadoForm 
from django.contrib import messages
from django.db.models import Avg
from django.http import HttpResponse
import io 
from io import BytesIO
from collections import defaultdict
import json
import logging
from django.http import JsonResponse
from django.db.models import Q  # Agrega esta línea
from django.db import models


# ============================================================ MODULO LOGIN ==============================================================================

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Verificar si es un alumno y su estado de admisión
            if hasattr(user, 'alumno'):
                alumno = Alumno.objects.get(user=user)
                if alumno.estado_admision == 'Pendiente':
                    # Si el estado es "Pendiente", no permitir el login
                    messages.error(request, 'Su estado de admisión está pendiente. No puede acceder al sistema.')
                    return render(request, 'login.html')  # Volver a mostrar el formulario de login
                
                # Si el estado no es "Pendiente", permitir el login
                login(request, user)
                return redirect('alumno_home')  # Redirigir al alumno

            # Verificar si es profesor
            elif hasattr(user, 'profesor'):
                login(request, user)
                return redirect('profesor')  # Redirigir al profesor

            # Verificar si es apoderado
            elif hasattr(user, 'apoderado'):
                login(request, user)
                return redirect('apoderado_view')  # Redirigir al apoderado

            # Otras redirecciones según roles adicionales
            else:
                login(request, user)
                return redirect('default')  # Redirigir a una página predeterminada si no es alumno, profesor o apoderado
        else:
            # Si las credenciales son inválidas
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'login.html')

# =================================================================== DASHBOARD DE PROFESOR ==============================================================

@login_required
def profesor_dashboard(request):
    return render(request, 'profesor.html')  # Renderiza el dashboard del profesor

# =================================================================== profesor cursos =====================================================================
@login_required
def profesor_cursos(request):
    profesor = Profesor.objects.get(user=request.user)  # Obtener el profesor basado en el usuario logueado
    cursos = Curso.objects.filter(profesor=profesor)  # Obtener los cursos asociados a ese profesor
    context = {
        'profesor': profesor,
        'cursos': cursos,
    }
    return render(request, 'profesorCursos.html', context)

# ================================================================== USER DB ===============================================================================
def crear_usuario_db(request):
    # Crear un usuario si no existe
    user = User.objects.create_user(username='Orly', password='contraseña', email='orlandone@gmail.com')

# ======================================================== Crear un profesor ===============================================================================

    profesor = Profesor.objects.create(user=user, nombre='Orly', apellido='APELLIDO', email='orlandone@gmail.com')
    return redirect(login)

# ======================================================= VIEWS PROFESOR LIBRO =============================================================================

@login_required
def libro_clases(request, curso_id):
    # Obtener el curso específico con el ID proporcionado
    curso = get_object_or_404(Curso, id=curso_id)
    
    # Pasar los datos del curso a la plantilla
    context = {
        'curso': curso,
    }
    # Renderizar la plantilla 'profesorLibro.html'
    return render(request, 'profesorLibro.html', context)

# ================================================================= REGISTRAR ASISTENCIA ===================================================================

@login_required
def registrar_asistencia(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    
    # Filtra solo los alumnos aprobados
    alumnos_aprobados = Alumno.objects.filter(curso=curso, estado_admision='Aprobado')

    if not alumnos_aprobados.exists():
        messages.warning(request, f"No hay alumnos aprobados asociados al curso {curso.nombre}.")
        return redirect('profesor_cursos')  # Redirigir a otra vista si no hay alumnos aprobados

    if request.method == 'POST':
        # Crear un nuevo objeto Asistencia
        asistencia = Asistencia(curso=curso, fecha=date.today())
        asistencia.save()  # Guarda el objeto Asistencia antes de agregar a los alumnos

        for alumno in alumnos_aprobados:
            asistencia_estado = request.POST.get(f'asistencia_{alumno.id}')
            if asistencia_estado == 'presente':
                asistencia.alumnos_presentes.add(alumno)
            elif asistencia_estado == 'ausente':
                asistencia.alumnos_ausentes.add(alumno)
            elif asistencia_estado == 'justificado':
                asistencia.alumnos_justificados.add(alumno)

        asistencia.save()  # Guarda los cambios después de agregar los alumnos

        messages.success(request, "Asistencia registrada exitosamente.")
        return redirect('registrar_asistencia', curso_id=curso.id)  # Redirigir a la misma vista con curso_id

    return render(request, 'registrarAsistencia.html', {
        'curso': curso,
        'alumnos_aprobados': alumnos_aprobados,
    })



#=============================================================== REGISTRAR CALIFICACIONES ====================================================================

@login_required
def registrar_calificaciones(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    errores = {}
    form_list = {}

    # Filtramos solo los alumnos aprobados
    alumnos_aprobados = Alumno.objects.filter(curso=curso, estado_admision='Aprobado')

    if request.method == 'POST':
        for alumno in alumnos_aprobados:
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
        # Crea formularios para cada alumno aprobado
        form_list = {alumno: CalificacionForm(prefix=str(alumno.id)) for alumno in alumnos_aprobados}

    return render(request, 'registrarCalificaciones.html', {
        'curso': curso,
        'form_list': form_list,
        'errores': errores
    })



# =================================================== REGISTRO ACADEMICO =====================================================================================

@login_required
def registro_academico(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    
    # Filtrar solo alumnos aprobados
    alumnos_aprobados = Alumno.objects.filter(curso=curso, estado_admision='Aprobado')
    
    calificaciones = Calificacion.objects.filter(curso=curso)
    asistencias = Asistencia.objects.filter(curso=curso)

    # Construir un diccionario para mapear alumnos a sus calificaciones
    calificaciones_por_alumno = {}
    promedios_por_alumno = {}
    asistencias_por_alumno = {}

    for alumno in alumnos_aprobados:
        # Filtrar calificaciones del alumno
        calificaciones_alumno = calificaciones.filter(alumno=alumno)
        calificaciones_por_alumno[alumno] = calificaciones_alumno

        # Calcular el promedio de calificaciones
        promedio = calificaciones_alumno.aggregate(Avg('nota'))['nota__avg'] or 0
        promedios_por_alumno[alumno] = round(promedio, 2)

        # Obtener asistencias para cada alumno, incluyendo justificadas
        asistencias_alumno = (
            asistencias.filter(alumnos_presentes=alumno) |
            asistencias.filter(alumnos_ausentes=alumno) |
            asistencias.filter(alumnos_justificados=alumno)
        )
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

# ============================================ generar informe en pdf para el profesor por alumno ================================================================
@login_required
def alumno_detalle(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    cursos = alumno.curso_set.all()
    # Diccionarios para almacenar datos organizados por curso
    calificaciones_por_curso = {}
    promedios_por_curso = {}
    asistencias_por_curso = {}

    for curso in cursos:
        calificaciones_curso = Calificacion.objects.filter(alumno=alumno, curso=curso)
        calificaciones_por_curso[curso] = calificaciones_curso

        # Calcular promedio
        promedio = calificaciones_curso.aggregate(Avg('nota'))['nota__avg'] or 0
        promedios_por_curso[curso] = promedio

        asistencias_curso = Asistencia.objects.filter(Q(alumnos_presentes=alumno) | Q(alumnos_ausentes=alumno), curso=curso)
        asistencias_por_curso[curso] = asistencias_curso

    # Convertir los datos a un formato adecuado para JSON
    data = {
        'alumno': {
            'nombre': alumno.nombre,
            'apellido': alumno.apellido,
            # Agrega aquí otros campos del modelo Alumno que quieras incluir
        },
        'cursos': [
            {
                'nombre': curso.nombre,
                'profesor': curso.profesor.nombre,  # Asumiendo que Profesor tiene un campo nombre
                'calificaciones': [
                    {'fecha': calificacion.fecha, 'nota': calificacion.nota} for calificacion in calificaciones_curso
                ],
                'promedio': promedio,
                'asistencias': [asistencia.fecha for asistencia in asistencias_curso],  # Ejemplo de cómo incluir asistencias
            } for curso in cursos
        ]
    }

    return render(request, 'Profe_generar_informes.html', {'data': data})

    
# =============================================================== OBSERVACIONES =========================================================================
@login_required
def observaciones(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    observaciones = Observacion.objects.filter(curso=curso)

    # Filtra solo los alumnos aprobados
    alumnos_aprobados = Alumno.objects.filter(curso=curso, estado_admision='Aprobado')

    if request.method == 'POST':
        if 'eliminar' in request.POST:
            observacion_id = request.POST.get('observacion_id')
            observacion = get_object_or_404(Observacion, id=observacion_id)
            observacion.delete()
            return redirect('observaciones', curso_id=curso.id)  # Redirigir después de eliminar

        # Lógica para agregar una nueva observación
        form = ObservacionForm(request.POST)
        form.fields['alumno'].queryset = alumnos_aprobados  # Filtrar alumnos aprobados
        if form.is_valid():
            observacion = form.save(commit=False)
            observacion.curso = curso  # Asociar la observación al curso
            observacion.save()
            return redirect('observaciones', curso_id=curso.id)  # Redirigir después de guardar
    else:
        form = ObservacionForm()
        form.fields['alumno'].queryset = alumnos_aprobados  # Filtrar alumnos aprobados

    return render(request, 'observaciones.html', {
        'curso': curso,
        'observaciones': observaciones,
        'form': form,
    })


# ============================================================= DASHBOARD ALUMNOS =======================================================================

def alumno_dashboard(request):
    return render(request, 'alumno.html')

# ===================================================== Vista para la consulta de asistencia ============================================================
@login_required
def alumno_consulta_asistencia(request):
    # Obtener el objeto Alumno asociado al usuario actual
    alumno = get_object_or_404(Alumno, user=request.user)
    
    # Verificar el estado de admisión del alumno
    if alumno.estado_admision != 'Aprobado':
        messages.error(request, 'Su estado de admisión no le permite acceder a la consulta de asistencia.')
        return redirect('alumno_home')

    # Obtener los cursos en los que está inscrito el alumno
    cursos = Curso.objects.filter(alumnos=alumno)
    asistencias_data = []

    # Recorremos los cursos del alumno para obtener la información de asistencia
    for curso in cursos:
        total_clases = Asistencia.objects.filter(curso=curso).count()  # Total de clases (días)
        
        # Obtener asistencias como presente, ausente y justificado
        asistencias_presente = Asistencia.objects.filter(curso=curso, alumnos_presentes=alumno).count()
        asistencias_justificado = Asistencia.objects.filter(curso=curso, alumnos_justificados=alumno).count()
        asistencias_ausente = Asistencia.objects.filter(curso=curso, alumnos_ausentes=alumno).count()

        # Se suma el presente con el justificado para obtener el total de asistencia válida
        total_asistencia_valida = asistencias_presente + asistencias_justificado
        porcentaje_asistencia = (total_asistencia_valida / total_clases * 100) if total_clases > 0 else 0

        asistencias_data.append({
            'curso': curso.nombre,
            'asignatura': curso.asignatura,
            'total_clases': total_clases,
            'asistencia_valida': total_asistencia_valida,
            'ausencias': asistencias_ausente,
            'porcentaje_asistencia': round(porcentaje_asistencia, 2)
        })

    # Renderizar el template con los datos de asistencia
    return render(request, 'alumnoConsuAsis.html', {'asistencias_data': asistencias_data})



# =========================================================== Vista para la consulta de notas ==========================================================================

@login_required
def alumno_consulta_notas(request):
    # Obtener el alumno actual (suponiendo que el usuario esté autenticado)
    alumno = Alumno.objects.get(user=request.user)

    # Obtener los cursos del alumno
    cursos = Curso.objects.filter(alumnos=alumno).prefetch_related('calificacion_set')

    # Agregar el promedio de notas para cada curso
    cursos_con_promedios = []
    for curso in cursos:
        calificaciones = Calificacion.objects.filter(curso=curso, alumno=alumno)
        if calificaciones.exists():
            promedio = calificaciones.aggregate(average_nota=models.Avg('nota'))['average_nota']
        else:
            promedio = None  # No hay notas disponibles
        cursos_con_promedios.append({
            'curso': curso,
            'calificaciones': calificaciones,
            'promedio': promedio
        })

    return render(request, 'alumnoConsuNotas.html', {'cursos_con_promedios': cursos_con_promedios})


# ===================================================================== alumno home ====================================================================================
@login_required
def alumno_home(request):
    # Aquí puedes obtener más información del alumno si es necesario
    alumno = request.user.alumno  # Si tienes un modelo 'Alumno' relacionado con 'User'
    
    context = {
        'alumno': alumno
    }
    return render(request, 'alumno.html', context)

# ===================================================================== APODERADO =====================================================================================
def apoderado_view(request):
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

            # la asistencia toma como presente el justificado
            total_asistencia = asistencias_presente + asistencias_justificado
            porcentaje_asistencia = (total_asistencia / total_clases * 100) if total_clases > 0 else 0

            asistencias_data.append({
                'nombre_alumno': alumno.nombre,  
                'curso': curso.nombre,
                'asignatura': curso.asignatura,
                'total_clases': total_clases,
                'asistencia': total_asistencia,
                'porcentaje_asistencia': round(porcentaje_asistencia, 2)
            })

    return render(request, 'apoderadoConsuAsis.html', {'asistencias_data': asistencias_data})

# =====================================================================================================================================================================

@login_required
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

    # Se calcula el promedio de notas de los alumnos
    for curso in cursos:
        calificaciones_curso = calificaciones.filter(curso=curso)
        total_notas = sum(c.nota for c in calificaciones_curso if c.nota is not None)
        count_notas = calificaciones_curso.count()
        curso.promedio = round(total_notas / count_notas, 2) if count_notas > 0 else 0  # Redondea a 2 decimales

    context = {
        'calificaciones': calificaciones,
        'cursos': cursos,
        'alumno': alumno
    }
    return render(request, 'apoderadoConsuNotas.html', context)

@login_required
def apoderadoMatri(request):
    return render(request, 'apoderadoMatri.html')


# ==================================================================== DIRECTOR =========================================================================================
#@login_required
def director_dashboard(request):
    return render(request, 'director.html') 
#@login_required
def directorMenu(request):
    # Aquí podrías agregar lógica para consultar informes si es necesario
    return render(request, 'directorMenu.html')

from django.shortcuts import render, redirect
from .models import Curso
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def director_plani(request):
    cursos = Curso.objects.all()

    if request.method == "POST":
        # Procesar la edición del curso
        curso_id = request.POST.get("curso_id")
        asignatura = request.POST.get("asignatura")
        dias = request.POST.get("dias")
        hora = request.POST.get("hora")
        sala = request.POST.get("sala")

        curso = Curso.objects.get(id=curso_id)
        curso.asignatura = asignatura
        curso.dias = dias
        curso.hora = hora
        curso.sala = sala
        curso.save()

        return JsonResponse({'success': True})

    return render(request, 'directorPlani.html', {'cursos': cursos})


def informes_academicos(request):
    cursos = Curso.objects.all()  # Obtener todos los cursos
    informes = []

    for curso in cursos:
        alumnos = curso.alumnos.all()  # Obtener todos los alumnos del curso
        total_alumnos = alumnos.count()  # Contar el número de alumnos inscritos
        
        # Calcular el promedio de calificaciones para el curso
        promedio_notas = Calificacion.objects.filter(alumno__in=alumnos).aggregate(Avg('nota'))['nota__avg'] or 0
        
        # Calcular el total de días de asistencia y asistencias
        total_asistencias = Asistencia.objects.filter(alumnos_presentes__in=alumnos).count()
        total_dias = Asistencia.objects.filter(curso=curso).count()
        
        # Verificar que no haya división por cero
        if total_alumnos > 0 and total_dias > 0:
            promedio_asistencia = (total_asistencias / (total_alumnos * total_dias)) * 100
        else:
            promedio_asistencia = 0  # Si no hay alumnos o días, el promedio de asistencia es 0
        
        # Crear un diccionario con la información del informe para este curso
        informes.append({
            'curso': curso,
            'total_alumnos': total_alumnos,
            'promedio_notas': round(promedio_notas, 1),  # Redondear a un decimal
            'promedio_asistencia': round(promedio_asistencia, 1)  # Redondear a un decimal
        })

    context = {
        'informes': informes
    }

    return render(request, 'direInfoAca.html', context)

def informes_finanzas(request):
    return render(request, 'direInfoFinan.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Curso  # Asegúrate de importar tu modelo

@csrf_exempt  # Solo si es necesario; no recomendado para producción sin protección
def update_curso(request):
    if request.method == 'POST':
        curso_id = request.POST.get('curso_id')
        hora = request.POST.get('hora')
        sala = request.POST.get('sala')

        try:
            curso = Curso.objects.get(id=curso_id)
            curso.hora = hora
            curso.sala = sala
            curso.save()

            return JsonResponse({'status': 'success'})
        except Curso.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Curso no encontrado'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


# ========================================================================== ADMISION Y MATRICULA ============================================================================================

def gestionar_estudiantes(request):
    alumnos_pendientes = Alumno.objects.filter(estado_admision='Pendiente')
    alumnos_aprobados = Alumno.objects.filter(estado_admision='Aprobado')
    
    context = {
        'alumnos_pendientes': alumnos_pendientes,
        'alumnos_aprobados': alumnos_aprobados,
    }
    
    return render(request, 'gestionar_estudiantes.html', context)



def agregar_alumno(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            # Primero crea el usuario
            user = User.objects.create_user(
                username=form.cleaned_data['email'],  # Puedes ajustar esto si quieres usar otro campo como username
                password=form.cleaned_data['password'],  # Asegúrate de que la contraseña esté en el formulario
                email=form.cleaned_data['email'],
            )
            # Luego crea el Alumno
            alumno = Alumno(
                user=user,
                nombre=form.cleaned_data['nombre'],
                apellido=form.cleaned_data['apellido'],
                email=form.cleaned_data['email'],
                apoderado=form.cleaned_data['apoderado'],  # Este campo ya está en el formulario
                estado_admision=form.cleaned_data['estado_admision'],  # Este campo ya está en el formulario
                curso=form.cleaned_data['curso'],  # Asignar el curso
            )
            alumno.save()  # Guarda el alumno en la base de datos
            return redirect('gestionar_estudiantes')  # Redirige a la lista de estudiantes
    else:
        form = AlumnoForm()  # Si no es POST, crea un nuevo formulario
    
    return render(request, 'agregar_alumno.html', {'form': form})  # Renderiza la plantilla con el formulario


def eliminar_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    alumno.delete()  # Eliminar el alumno
    return redirect('gestionar_estudiantes')  # Redirige a la lista de estudiantes

def actualizar_matricula(request, id):
    alumno = get_object_or_404(Alumno, id=id)

    if request.method == 'POST':
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Matrícula actualizada con éxito.')
            return redirect('gestionar_estudiantes')  # Redirigir a la lista de estudiantes
    else:
        form = AlumnoForm(instance=alumno)

    return render(request, 'actualizar_matricula.html', {'form': form, 'alumno': alumno})




def panel_admision(request):
    alumnos = Alumno.objects.all()  # Obtiene todos los alumnos
    return render(request, 'panel_admision.html', {'alumnos': alumnos})


# ===========================================================================================================================================================================================
