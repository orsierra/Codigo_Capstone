# views.py
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Curso, Profesor,Asistencia, Calificacion, Informe, Observacion, Alumno, Apoderado, Curso, InformeFinanciero,InformeAcademico,Director, Contrato,AsisFinanza, AsisMatricula, Establecimiento,Subdirector
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from datetime import date
from django.utils import timezone
from .forms import CalificacionForm, ObservacionForm, AlumnoForm, InformeFinancieroForm, ApoderadoForm, ContratoForm
from django.contrib import messages
from django.db.models import Avg
from django.http import HttpResponse
from django.http import JsonResponse
from django.db.models import Q 
from django.db import models
#=====================================================
from django.template.loader import render_to_string
from weasyprint import HTML
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django.db.models import Count
from django.http import Http404

# ============================================================ MODULO INICIO ==============================================================================


def inicio(request): 
    return render(request, 'inicio.html')

def quienes_somos(request):
    return render(request, 'quienes_somos.html')

# Modulo Login
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'alumno'):
                alumno = Alumno.objects.get(user=user)
                if alumno.estado_admision == 'Pendiente':
                    messages.error(request, 'Su estado de admisión está pendiente. No puede acceder al sistema.')
                    return render(request, 'login.html')
                login(request, user)
                return redirect('alumno_dashboard')

            if hasattr(user, 'profesor'):
                profesor = user.profesor  # Obtener el objeto profesor
                establecimiento_id = profesor.establecimiento_id  # Asegúrate de que el modelo Profesor tenga un campo `establecimiento`
                login(request, user)
                return redirect('profesor', establecimiento_id=establecimiento_id)  # Pasa el establecimiento_id aquí

            elif hasattr(user, 'apoderado'):
                login(request, user)
                return redirect('apoderado_view')

            elif hasattr(user, 'director'):
                login(request, user)
                return redirect('director_dashboard')
            
            elif hasattr(user, 'subdirector'):
                login(request, user)
                return redirect('subdirector_home')

            elif hasattr(user, 'asisfinanza'):
                login(request, user)
                return redirect('panel_asisAdminFinan')

            elif hasattr(user, 'asismatricula'):
                login(request, user)
                return redirect('panel_admision')
            else:
                login(request, user)
                return redirect('login')

        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'login.html')

# Logout
def logout_view(request):
    logout(request)
    return redirect('inicio') 

# Dashboard de profesor
@login_required
def profesor_dashboard(request, establecimiento_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    return render(request, 'profesor.html', {'establecimiento': establecimiento})

# Profesor - cursos asignados
@login_required
def profesor_cursos(request, establecimiento_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    profesor = Profesor.objects.get(user=request.user)  # Obtener el profesor basado en el usuario logueado
    cursos = Curso.objects.filter(profesor=profesor, establecimiento=establecimiento)  # Obtener los cursos asociados a ese profesor y establecimiento
    
    context = {
        'profesor': profesor,
        'cursos': cursos,
        'establecimiento': establecimiento,
    }
    return render(request, 'profesorCursos.html', context)


# Crear usuario en la DB (ejemplo)
def crear_usuario_db(request):
    user = User.objects.create_user(username='Orly', password='contraseña', email='orlandone@gmail.com')
    establecimiento = Establecimiento.objects.get(nombre="Colegio Nuevos Horizontes")
    profesor = Profesor.objects.create(user=user, nombre='Orly', apellido='APELLIDO', email='orlandone@gmail.com', establecimiento=establecimiento)
    return redirect('login')

# Libro de clases del profesor
@login_required
def libro_clases(request, establecimiento_id, curso_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=establecimiento)
    alumnos = Alumno.objects.filter(curso=curso)  # Filtra los alumnos en el curso

    context = {
        'curso': curso,
        'establecimiento': establecimiento,
        'alumnos': alumnos,
    }
    return render(request, 'profesorLibro.html', context)


# Registrar asistencia
@login_required
def registrar_asistencia(request, establecimiento_id, curso_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=establecimiento)
    alumnos_aprobados = Alumno.objects.filter(curso=curso, estado_admision='Aprobado', establecimiento=establecimiento)

    if not alumnos_aprobados.exists():
        messages.warning(request, f"No hay alumnos aprobados asociados al curso {curso.nombre}.")
        return redirect('profesor_cursos', establecimiento_id=establecimiento_id)

    if request.method == 'POST':
        asistencia = Asistencia(curso=curso, fecha=date.today(), establecimiento=establecimiento)
        asistencia.save()

        for alumno in alumnos_aprobados:
            asistencia_estado = request.POST.get(f'asistencia_{alumno.id}')
            if asistencia_estado == 'presente':
                asistencia.alumnos_presentes.add(alumno)
            elif asistencia_estado == 'ausente':
                asistencia.alumnos_ausentes.add(alumno)
            elif asistencia_estado == 'justificado':
                asistencia.alumnos_justificados.add(alumno)

        asistencia.save()
        messages.success(request, "Asistencia registrada exitosamente.")
        return redirect('registrar_asistencia', establecimiento_id=establecimiento_id, curso_id=curso.id)

    return render(request, 'registrarAsistencia.html', {
    'curso': curso,
    'alumnos_aprobados': alumnos_aprobados,
    'establecimiento': establecimiento,
    'establecimiento_id': establecimiento_id,  # Asegúrate de pasar esto
})


# Registrar calificaciones
@login_required
def registrar_calificaciones(request, establecimiento_id, curso_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=establecimiento)
    errores = {}
    form_list = {}

    alumnos_aprobados = Alumno.objects.filter(curso=curso, estado_admision='Aprobado', establecimiento=establecimiento)

    if request.method == 'POST':
        for alumno in alumnos_aprobados:
            form = CalificacionForm(request.POST, prefix=str(alumno.id))
            if form.is_valid():
                calificacion = form.save(commit=False)
                calificacion.alumno = alumno
                calificacion.curso = curso
                calificacion.establecimiento = establecimiento
                calificacion.save()
            else:
                errores[alumno] = form.errors

        if not errores:
            messages.success(request, "Se han guardado los cambios exitosamente.")
            return redirect('registrar_calificaciones', establecimiento_id=establecimiento_id, curso_id=curso_id)

    else:
        form_list = {alumno: CalificacionForm(prefix=str(alumno.id)) for alumno in alumnos_aprobados}

    return render(request, 'registrarCalificaciones.html', {
        'curso': curso,
        'form_list': form_list,
        'errores': errores,
        'establecimiento': establecimiento,
    })

# Registro académico
@login_required
def registro_academico(request, establecimiento_id, curso_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=establecimiento)
    
    alumnos_aprobados = Alumno.objects.filter(curso=curso, estado_admision='Aprobado', establecimiento=establecimiento)
    calificaciones = Calificacion.objects.filter(curso=curso)
    asistencias = Asistencia.objects.filter(curso=curso)

    calificaciones_por_alumno = {}
    promedios_por_alumno = {}
    asistencias_por_alumno = {}

    for alumno in alumnos_aprobados:
        calificaciones_alumno = calificaciones.filter(alumno=alumno)
        calificaciones_por_alumno[alumno] = calificaciones_alumno
        promedio = calificaciones_alumno.aggregate(Avg('nota'))['nota__avg'] or 0
        promedios_por_alumno[alumno] = round(promedio, 2)
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
        'establecimiento': establecimiento,
    }
    return render(request, 'registroAcademico.html', context)

# Generar informes
@login_required
def generar_informes(request, establecimiento_id, curso_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=establecimiento)
    alumnos_aprobados = Alumno.objects.filter(curso=curso, estado_admision='Aprobado', establecimiento=establecimiento)

    return render(request, 'Profe_generar_informes.html', {
        'curso': curso, 
        'alumnos_aprobados': alumnos_aprobados,
        'establecimiento': establecimiento,
    })

# Alumno detalle para generar informe en PDF
@login_required
def alumno_detalle(request, establecimiento_id, alumno_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    alumno = get_object_or_404(Alumno, id=alumno_id, establecimiento=establecimiento)
    curso = alumno.curso  # Esto obtiene el curso del alumno
    calificaciones = Calificacion.objects.filter(alumno=alumno, curso=curso)
    promedio = calificaciones.aggregate(Avg('nota'))['nota__avg'] or 0
    asistencias = Asistencia.objects.filter(curso=curso).filter(alumnos_presentes=alumno)
    ausencias = Asistencia.objects.filter(curso=curso).filter(alumnos_ausentes=alumno)
    justificaciones = Asistencia.objects.filter(curso=curso).filter(alumnos_justificados=alumno)

    context = {
        'alumno': alumno,
        'calificaciones': calificaciones,
        'asistencias': asistencias,
        'ausencias': ausencias,
        'justificaciones': justificaciones,
        'promedio': promedio,
        'establecimiento': establecimiento,
        'curso': curso,  # Asegúrate de pasar el objeto curso al contexto
    }
    return render(request, 'alumno_detalle.html', context)


# Descargar PDF de alumno
@login_required
def descargar_pdf_alumno(request, establecimiento_id, alumno_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    alumno = get_object_or_404(Alumno, id=alumno_id, establecimiento=establecimiento)
    calificaciones = Calificacion.objects.filter(alumno=alumno)
    asistencias = Asistencia.objects.filter(alumnos_presentes=alumno)
    ausencias = Asistencia.objects.filter(alumnos_ausentes=alumno)
    justificaciones = Asistencia.objects.filter(alumnos_justificados=alumno)
    promedio = calificaciones.aggregate(Avg('nota'))['nota__avg'] or 0

    context = {
        'alumno': alumno,
        'calificaciones': calificaciones,
        'asistencias': asistencias,
        'ausencias': ausencias,
        'justificaciones': justificaciones,
        'promedio': promedio,
        'establecimiento': establecimiento,
    }

    html_string = render_to_string('alumno_detalle.html', context)
    html = HTML(string=html_string)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{alumno.nombre}_{alumno.apellido}_detalle.pdf"'
    html.write_pdf(response)

    return response

# =============================================================== OBSERVACIONES =========================================================================
@login_required
def observaciones(request, establecimiento_id, alumno_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    alumno = get_object_or_404(Alumno, id=alumno_id)
    curso = alumno.curso  # Obtener el curso del alumno
    observaciones = Observacion.objects.filter(curso=curso)

    alumnos_aprobados = Alumno.objects.filter(curso=curso, estado_admision='Aprobado')

    if request.method == 'POST':
        if 'eliminar' in request.POST:
            observacion_id = request.POST.get('observacion_id')
            observacion = get_object_or_404(Observacion, id=observacion_id)
            observacion.delete()
            return redirect('observaciones', establecimiento_id=establecimiento.id, curso_id=curso.id)

        # Lógica para agregar una nueva observación
        form = ObservacionForm(request.POST)
        form.fields['alumno'].queryset = alumnos_aprobados  # Filtrar alumnos aprobados
        if form.is_valid():
            observacion = form.save(commit=False)
            observacion.curso = curso  # Asociar la observación al curso
            observacion.save()
            return redirect('observaciones', establecimiento_id=establecimiento.id, curso_id=curso.id)
    else:
        form = ObservacionForm()
        form.fields['alumno'].queryset = alumnos_aprobados  # Filtrar alumnos aprobados

    return render(request, 'observaciones.html', {
        'curso': curso,
        'establecimiento': establecimiento,
        'observaciones': observaciones,
        'form': form,
    })



# ============================================================= Dashboard de Alumno ==================================================

@login_required
def alumno_dashboard(request):
    return render(request, 'alumno.html')


# ===================================================== Consulta de Asistencia del Alumno ============================================

@login_required
def alumno_consulta_asistencia(request):
    # Obtener el objeto Alumno asociado al usuario actual
    alumno = get_object_or_404(Alumno, user=request.user)
    
    # Verificar el estado de admisión del alumno
    if alumno.estado_admision != 'Aprobado':
        messages.error(request, 'Su estado de admisión no le permite acceder a la consulta de asistencia.')
        return redirect('alumno_home')

    asistencias_data = []

    # Obtener los cursos en los que está inscrito el alumno
    cursos = alumno.cursos_asignados.all()

    for curso in cursos:
        fechas_presentes = set(Asistencia.objects.filter(curso=curso, alumnos_presentes=alumno).values_list('fecha', flat=True))
        fechas_ausentes = set(Asistencia.objects.filter(curso=curso, alumnos_ausentes=alumno).values_list('fecha', flat=True))
        fechas_justificados = set(Asistencia.objects.filter(curso=curso, alumnos_justificados=alumno).values_list('fecha', flat=True))

        fechas_totales = fechas_presentes | fechas_ausentes | fechas_justificados
        total_clases = len(fechas_totales)

        total_asistencia = len(fechas_presentes) + len(fechas_justificados)
        porcentaje_asistencia = (total_asistencia / total_clases * 100) if total_clases > 0 else 0

        asistencias_data.append({
            'curso': curso.nombre,
            'asignatura': curso.asignatura,
            'total_clases': total_clases,
            'asistencia': total_asistencia,
            'porcentaje_asistencia': round(porcentaje_asistencia, 2),
        })

    return render(request, 'alumnoConsuAsis.html', {'asistencias_data': asistencias_data})


# =========================================================== Consulta de Notas del Alumno ============================================================

@login_required
def alumno_consulta_notas(request):
    alumno = get_object_or_404(Alumno, user=request.user)
    cursos = Curso.objects.filter(alumnos=alumno).prefetch_related('calificacion_set')

    cursos_con_promedios = []
    for curso in cursos:
        calificaciones = Calificacion.objects.filter(curso=curso, alumno=alumno)
        promedio = calificaciones.aggregate(average_nota=models.Avg('nota'))['average_nota'] if calificaciones.exists() else None

        cursos_con_promedios.append({
            'curso': curso,
            'calificaciones': calificaciones,
            'promedio': promedio
        })

    return render(request, 'alumnoConsuNotas.html', {'cursos_con_promedios': cursos_con_promedios})


# ===================================================================== Home del Alumno ====================================================================

@login_required
def alumno_home(request):
    alumno = request.user.alumno
    context = {
        'alumno': alumno
    }
    return render(request, 'alumno.html', context)


# ===================================================================== Vista del Apoderado ==================================================================

@login_required
def apoderado_view(request):
    return render(request, 'apoderado.html')


#============================================================================= Consulta de Asistencia del Apoderado =========================================================================================

@login_required
def apoderadoConsuAsis(request):
    apoderado = get_object_or_404(Apoderado, user=request.user)
    alumnos = Alumno.objects.filter(apoderado=apoderado, estado_admision='Aprobado')
    asistencias_data = {}

    for alumno in alumnos:
        cursos = alumno.cursos_asignados.all()
        asistencias_data[alumno] = []

        for curso in cursos:
            fechas_presentes = set(Asistencia.objects.filter(curso=curso, alumnos_presentes=alumno).values_list('fecha', flat=True))
            fechas_ausentes = set(Asistencia.objects.filter(curso=curso, alumnos_ausentes=alumno).values_list('fecha', flat=True))
            fechas_justificados = set(Asistencia.objects.filter(curso=curso, alumnos_justificados=alumno).values_list('fecha', flat=True))

            fechas_totales = fechas_presentes | fechas_ausentes | fechas_justificados
            total_clases = len(fechas_totales)

            total_asistencia = len(fechas_presentes) + len(fechas_justificados)
            porcentaje_asistencia = (total_asistencia / total_clases * 100) if total_clases > 0 else 0

            asistencias_data[alumno].append({
                'curso': curso,
                'total_clases': total_clases,
                'asistencia': total_asistencia,
                'porcentaje_asistencia': round(porcentaje_asistencia, 2),
            })

    context = {
        'alumnos': alumnos,
        'asistencias_data': asistencias_data,
    }
    return render(request, 'apoderadoConsuAsis.html', context)


# ============================================================================== Consulta de Notas del Apoderado ============================================================================

@login_required
def apoderadoConsuNotas(request):
    apoderado = get_object_or_404(Apoderado, user=request.user)
    alumnos = Alumno.objects.filter(apoderado=apoderado, estado_admision="Aprobado")

    alumnos_data = []

    for alumno in alumnos:
        alumno_info = {
            'alumno': alumno,
            'cursos': []
        }

        cursos = Curso.objects.filter(calificacion__alumno=alumno).distinct()
        
        for curso in cursos:
            calificaciones_curso = Calificacion.objects.filter(alumno=alumno, curso=curso)
            total_notas = sum(c.nota for c in calificaciones_curso if c.nota is not None)
            count_notas = calificaciones_curso.count()
            promedio = round(total_notas / count_notas, 2) if count_notas > 0 else 0

            calificaciones_numeradas = [{'numero': i + 1, 'nota': calificacion.nota} for i, calificacion in enumerate(calificaciones_curso)]
            
            curso_info = {
                'curso': curso,
                'calificaciones': calificaciones_numeradas,
                'promedio': promedio
            }
            alumno_info['cursos'].append(curso_info)

        alumnos_data.append(alumno_info)

    context = {
        'alumnos_data': alumnos_data,
    }
    return render(request, 'apoderadoConsuNotas.html', context)


# ======================================================================= APODERADO OBSERVACIONES ================================================================================================

# ====================================================== Apoderado - Observaciones ======================================================

@login_required
def apoderado_observaciones(request):
    apoderado = get_object_or_404(Apoderado, user=request.user)
    alumnos_aprobados = Alumno.objects.filter(apoderado=apoderado, estado_admision="Aprobado")
    
    observaciones_data = []
    for alumno in alumnos_aprobados:
        observaciones_alumno = Observacion.objects.filter(alumno=alumno).select_related('curso')
        observaciones_data.append({
            'alumno': alumno,
            'observaciones': observaciones_alumno
        })

    return render(request, 'apoderadoObservaciones.html', {'observaciones_data': observaciones_data})


# ============================================================ Director - Dashboard =========================================================

@login_required
def director_dashboard(request):
    return render(request, 'director.html')


@login_required
def directorMenu(request):
    return render(request, 'directorMenu.html')


# ============================================================ Director - Planificación Académica =========================================================

@csrf_exempt
def director_plani(request):
    # Obtener el director autenticado y su establecimiento
    director = Director.objects.get(user=request.user)
    cursos = Curso.objects.filter(establecimiento=director.establecimiento)

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            curso_id = data.get("curso_id")
            hora = data.get("hora")
            sala = data.get("sala")

            # Buscar el curso específico dentro del establecimiento del director
            curso = cursos.get(id=curso_id)
            curso.hora = hora
            curso.sala = sala
            curso.save()

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return render(request, 'directorPlani.html', {'cursos': cursos})


# ====================================================== Director - Informes Académicos ======================================================

@login_required
def informes_academicos(request):
    # Obtiene el director que está autenticado
    director = get_object_or_404(Director, user=request.user)
    
    # Filtra los cursos que pertenecen al establecimiento del director
    cursos = Curso.objects.filter(establecimiento=director.establecimiento)
    
    # Prepara la lista de informes académicos solo para los cursos filtrados
    informes = []

    for curso in cursos:
        alumnos = curso.alumnos.all()
        total_alumnos = alumnos.count()
        promedio_notas = Calificacion.objects.filter(alumno__in=alumnos).aggregate(Avg('nota'))['nota__avg'] or 0
        total_asistencias = Asistencia.objects.filter(alumnos_presentes__in=alumnos).count()
        total_dias = Asistencia.objects.filter(curso=curso).count()

        promedio_asistencia = (total_asistencias / (total_alumnos * total_dias) * 100) if total_alumnos > 0 and total_dias > 0 else 0
        
        informes.append({
            'curso': curso,
            'total_alumnos': total_alumnos,
            'promedio_notas': round(promedio_notas, 1),
            'promedio_asistencia': round(promedio_asistencia, 1)
        })

    return render(request, 'direInfoAca.html', {'informes': informes})


# ====================================================== Director - Actualizar Curso ======================================================

@csrf_exempt
def update_curso(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            curso_id = data.get("curso_id")
            hora = data.get("hora")
            sala = data.get("sala")

            curso = Curso.objects.get(id=curso_id)
            curso.hora = hora
            curso.sala = sala
            curso.save()

            return JsonResponse({'success': True})
        except Curso.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Curso no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Método no permitido'}, status=405)


# ====================================================== Director - Informe Académico en PDF ======================================================

@login_required
def direcPdfInfoAca(request):
    # Obtiene el director autenticado
    director = get_object_or_404(Director, user=request.user)
    
    # Filtra los cursos que pertenecen al establecimiento del director
    cursos = Curso.objects.filter(establecimiento=director.establecimiento)
    
    # Genera los informes académicos para los cursos filtrados
    informes = []
    for curso in cursos:
        alumnos = curso.alumnos.all()
        total_alumnos = alumnos.count()
        promedio_notas = Calificacion.objects.filter(alumno__in=alumnos).aggregate(Avg('nota'))['nota__avg'] or 0
        total_asistencias = Asistencia.objects.filter(alumnos_presentes__in=alumnos).count()
        total_dias = Asistencia.objects.filter(curso=curso).count()

        promedio_asistencia = (total_asistencias / (total_alumnos * total_dias) * 100) if total_alumnos > 0 and total_dias > 0 else 0

        informes.append({
            'curso': curso,
            'total_alumnos': total_alumnos,
            'promedio_notas': round(promedio_notas, 1),
            'promedio_asistencia': round(promedio_asistencia, 1)
        })

    # Renderiza la plantilla con los informes académicos generados
    html_string = render_to_string('direInfoAca_pdf.html', {'informes': informes})
    
    # Genera y configura el PDF para la descarga
    html = HTML(string=html_string)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_academico.pdf"'
    
    # Escribe el contenido del PDF en la respuesta
    html.write_pdf(response)
    
    return response

# ====================================================== Director - Planificación Académica en PDF ======================================================

@login_required
def direcPdfPlanificacion(request):
    # Obtiene el director autenticado
    director = get_object_or_404(Director, user=request.user)
    
    # Filtra los cursos que pertenecen al establecimiento del director
    cursos = Curso.objects.filter(establecimiento=director.establecimiento)
    
    # Renderiza la plantilla con los cursos filtrados
    html_string = render_to_string('direcPdfPlanificacion_pdf.html', {'cursos': cursos})

    # Genera el PDF
    html = HTML(string=html_string)
    response = HttpResponse(html.write_pdf(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="planificacion_academica.pdf"'

    return response


# ====================================================== Informe Financiero - Vista y Gestión ======================================================

@login_required
def informe_financiero_view(request):
    # Obtiene el director autenticado
    director = get_object_or_404(Director, user=request.user)
    
    # Filtra los informes financieros por el establecimiento del director
    informes = InformeFinanciero.objects.filter(establecimiento=director.establecimiento)
    
    if request.method == 'POST':
        # Prellenar el establecimiento en el formulario
        form = InformeFinancieroForm(request.POST, initial={'establecimiento': director.establecimiento})
        if form.is_valid():
            informe = form.save(commit=False)
            informe.establecimiento = director.establecimiento  # Asigna el establecimiento del director
            informe.save()
            return redirect('informe_financiero')
    else:
        form = InformeFinancieroForm()
    
    return render(request, 'informe_financiero.html', {'form': form, 'informes': informes})


@login_required
def eliminar_informe_view(request, informe_id):
    # Obtiene el director autenticado
    director = get_object_or_404(Director, user=request.user)
    
    # Busca el informe en el establecimiento del director
    informe = get_object_or_404(InformeFinanciero, id=informe_id, establecimiento=director.establecimiento)
    
    if request.method == 'POST':
        informe.delete()
        return redirect('informe_financiero')
    
    return render(request, 'confirmar_eliminacion.html', {'informe': informe})


# ====================================================== Generar PDF de Informe Financiero ======================================================

@login_required
def generar_pdf_view(request):
    # Obtiene el director autenticado
    director = get_object_or_404(Director, user=request.user)
    
    # Filtra los informes financieros por el establecimiento del director
    informes = InformeFinanciero.objects.filter(establecimiento=director.establecimiento)
    
    # Contexto para el PDF
    context = {
        'titulo': 'Informe Finanzas Primer Semestre',
        'informes': informes,
    }

    # Genera el PDF
    html_string = render_to_string('pdf/informe_financiero_pdf.html', context)
    pdf = HTML(string=html_string).write_pdf()
    
    # Configura la respuesta HTTP para la descarga
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_financiero.pdf"'
    return response


# ====================================================== Admisión y Matrícula - Gestión de Estudiantes ======================================================

@login_required
def gestionar_estudiantes(request):
    alumnos_pendientes = Alumno.objects.filter(estado_admision='Pendiente')
    alumnos_aprobados = Alumno.objects.filter(estado_admision='Aprobado')
    
    return render(request, 'gestionar_estudiantes.html', {
        'alumnos_pendientes': alumnos_pendientes,
        'alumnos_aprobados': alumnos_aprobados,
    })


# =================================================== Admisión - Agregar Alumno ===================================================
@login_required
def agregar_alumno(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            if User.objects.filter(username=email).exists():
                form.add_error('email', 'Este correo electrónico ya está en uso.')
            else:
                try:
                    user = User.objects.create_user(username=email, password=password, email=email)
                    alumno = Alumno(
                        user=user,
                        nombre=form.cleaned_data['nombre'],
                        apellido=form.cleaned_data['apellido'],
                        email=email,
                        apoderado=form.cleaned_data['apoderado'],
                        estado_admision=form.cleaned_data['estado_admision'],
                        curso=form.cleaned_data['curso']
                    )
                    alumno.save()
                    curso = form.cleaned_data['curso']
                    curso.alumnos.add(alumno)
                    return redirect('gestionar_estudiantes')
                except IntegrityError:
                    form.add_error(None, 'Ocurrió un error al crear el usuario. Intenta nuevamente.')

    else:
        form = AlumnoForm()
    return render(request, 'agregar_alumno.html', {'form': form})


# =================================================== Admisión - Eliminar Alumno ===================================================
@login_required
def eliminar_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    alumno.delete()
    return redirect('gestionar_estudiantes')


# =================================================== Admisión - Actualizar Matrícula ===================================================
@login_required
def actualizar_matricula(request, id):
    alumno = get_object_or_404(Alumno, id=id)

    if request.method == 'POST':
        form = AlumnoForm(request.POST, instance=alumno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Matrícula actualizada con éxito.')
            return redirect('gestionar_estudiantes')
    else:
        form = AlumnoForm(instance=alumno)

    return render(request, 'actualizar_matricula.html', {'form': form, 'alumno': alumno})


# =================================================== Panel de Admisión ===================================================
@login_required
def panel_admision(request):
    alumnos = Alumno.objects.all()
    return render(request, 'panel_admision.html', {'alumnos': alumnos})


# =================================================== Asistente de Admisión y Finanzas - Dashboard ===================================================
@login_required
def asisAdminFinan_dashboard(request):
    return render(request, 'asisAdminFinan.html')


# =================================================== Asistente de Admisión y Finanzas - Gestión de Pagos ===================================================
@login_required
def ver_gestion_pagos_admision(request):
    alumnos = Alumno.objects.all()
    return render(request, 'asisAdmiFinan_gestion_pagos.html', {'alumnos': alumnos})


# =================================================== Asistente de Admisión y Finanzas - Agregar Alumno ===================================================
@login_required
def agregar_alumno_asis(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                email=form.cleaned_data['email']
            )
            alumno = Alumno(
                user=user,
                nombre=form.cleaned_data['nombre'],
                apellido=form.cleaned_data['apellido'],
                email=form.cleaned_data['email'],
                apoderado=form.cleaned_data['apoderado'],
                estado_admision=form.cleaned_data['estado_admision'],
                curso=form.cleaned_data['curso']
            )
            alumno.save()
            return redirect('asisAdmiFinan_gestion_pagos')
    else:
        form = AlumnoForm()
    return render(request, 'agregar_alumno_asis.html', {'form': form})


# =================================================== Asistente de Admisión y Finanzas - Eliminar Alumno ===================================================
@login_required
def eliminar_alumno_asis(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    alumno.delete()
    return redirect('asisAdmiFinan_gestion_pagos')


# =================================================== Asistente de Admisión y Finanzas - Editar Informe ===================================================
@login_required
def editar_informe_asis(request, id):
    alumno_instance = get_object_or_404(Alumno, id=id)
    contrato_instance = Contrato.objects.filter(alumno=alumno_instance).first()
    apoderado_instance = alumno_instance.apoderado

    if request.method == 'POST':
        form = ContratoForm(request.POST, instance=contrato_instance, alumno_instance=alumno_instance, apoderado_instance=apoderado_instance)
        
        if form.is_valid():
            apoderado_id = form.cleaned_data['apoderado_id']
            apoderado = Apoderado.objects.get(id=apoderado_id)
            contrato = form.save(commit=False)
            contrato.apoderado = apoderado
            contrato.alumno = alumno_instance
            contrato.save()
            return redirect('editar_informe_asis', id=alumno_instance.id)
    else:
        form = ContratoForm(instance=contrato_instance, alumno_instance=alumno_instance, apoderado_instance=apoderado_instance)

    return render(request, 'asis_edicion_info_pago.html', {'form': form, 'alumno': alumno_instance})


# =================================================== Asistente de Admisión y Finanzas - Generar PDF Contrato ===================================================
@login_required
def generar_pdf_contrato(request, id):
    alumno = get_object_or_404(Alumno, id=id)
    contrato = Contrato.objects.filter(alumno=alumno).first()

    if contrato is None:
        return HttpResponse("No se encontró el contrato asociado al alumno.", status=404)

    context = {'alumno': alumno, 'contrato': contrato}
    html_string = render_to_string('pdf/asis_pago.html', context)
    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pago_{alumno.nombre}_{alumno.apellido}.pdf"'
    return response


# =================================================== Subdirector - Panel de Inicio ===================================================
@login_required
def subdirector_home(request):
    return render(request, 'subdirector.html')


# =================================================== Subdirector - Consulta de Informes Académicos ===================================================
def consulta_informes_academicos(request):
    # Obtener el subdirector relacionado con el usuario autenticado
    subdirector = Subdirector.objects.get(user=request.user)

    # Filtrar los cursos que pertenecen al establecimiento del subdirector
    cursos = Curso.objects.filter(establecimiento=subdirector.establecimiento)
    
    return render(request, 'subdire_consulta_informes_academicos.html', {'cursos': cursos})


# =================================================== Subdirector - Gestión de Recursos Académicos ===================================================
@login_required
def gestion_recursos_academicos(request):
    # Obtener el subdirector relacionado con el usuario autenticado
    subdirector = Subdirector.objects.get(user=request.user)

    # Filtrar los cursos que pertenecen al establecimiento del subdirector
    cursos = Curso.objects.filter(establecimiento=subdirector.establecimiento).select_related('profesor')

    return render(request, 'gestion_recursos_academicos.html', {'cursos': cursos})

# =================================================== Subdirector - Detalle de Curso ===================================================
@login_required
def detalle_curso(request, curso_id):
    # Obtener el subdirector relacionado con el usuario autenticado
    subdirector = Subdirector.objects.get(user=request.user)
    
    # Obtener el curso solo si pertenece al establecimiento del subdirector
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=subdirector.establecimiento)
    
    # Filtrar los estudiantes que pertenecen al mismo establecimiento que el subdirector
    estudiantes = curso.alumnos.filter(establecimiento=subdirector.establecimiento)

    # Calcular el promedio de notas de cada estudiante
    estudiantes_con_promedio = [
        {
            'nombre': estudiante.nombre,
            'apellido': estudiante.apellido,
            'promedio_notas': round(Calificacion.objects.filter(alumno=estudiante, curso=curso).aggregate(promedio=Avg('nota'))['promedio'], 2) or "-"
        }
        for estudiante in estudiantes
    ]

    return render(request, 'detalle_curso.html', {'curso': curso, 'estudiantes': estudiantes_con_promedio})


# =================================================== Subdirector - Detalle de Curso en PDF ===================================================
@login_required
def detalle_curso_pdf(request, curso_id):
    # Obtener el subdirector relacionado con el usuario autenticado
    subdirector = Subdirector.objects.get(user=request.user)
    
    # Obtener el curso solo si pertenece al establecimiento del subdirector
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=subdirector.establecimiento)
    
    # Filtrar los estudiantes que pertenecen al establecimiento del subdirector
    estudiantes = curso.alumnos.filter(establecimiento=subdirector.establecimiento)
    
    # Calcular el promedio de notas de cada estudiante
    estudiantes_con_promedio = [
        {
            'nombre': estudiante.nombre,
            'apellido': estudiante.apellido,
            'promedio_notas': round(Calificacion.objects.filter(alumno=estudiante, curso=curso).aggregate(promedio=Avg('nota'))['promedio'], 2) or "-"
        }
        for estudiante in estudiantes
    ]
    
    # Renderizar el HTML y generar el PDF
    html_string = render_to_string('detalle_curso_pdf.html', {'curso': curso, 'estudiantes': estudiantes_con_promedio})
    pdf = HTML(string=html_string).write_pdf()

    # Devolver el archivo PDF como respuesta
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{curso.nombre}_reporte.pdf"'
    return response
# =================================================== Sostenedor - Información del Establecimiento ===================================================
@login_required
def sostenedor(request):
    # Obtener todos los establecimientos de la base de datos
    establecimientos = Establecimiento.objects.all()
    
    # Pasar los establecimientos al contexto
    contexto = {
        'establecimientos': establecimientos
    }
    
    return render(request, 'sostenedor.html', contexto)


@login_required
def establecimientos(request, establecimiento_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    total_salas = Curso.objects.filter(establecimiento=establecimiento).values('sala').distinct().count()
    total_alumnos = Alumno.objects.filter(establecimiento=establecimiento).count()
    total_cursos = Curso.objects.filter(establecimiento=establecimiento).count()
    total_profesores = Profesor.objects.filter(establecimiento=establecimiento).count()
    total_directores = Director.objects.filter(establecimiento=establecimiento).count()
    total_asistentes_matricula = AsisMatricula.objects.filter(establecimiento=establecimiento).count()
    total_asistentes_finanza = AsisFinanza.objects.filter(establecimiento=establecimiento).count()
    total_empleados = total_directores + total_profesores + total_asistentes_matricula + total_asistentes_finanza

    contexto = {
        'colegio_nombre': establecimiento.nombre,
        'total_salas': total_salas,
        'total_alumnos': total_alumnos,
        'total_cursos': total_cursos,
        'total_profesores': total_profesores,
        'total_empleados': total_empleados
    }

    return render(request, 'establecimientos.html', contexto)







