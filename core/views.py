# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Curso, BitacoraClase, Profesor,Asistencia, Calificacion, Informe, Observacion, Alumno, Apoderado, Curso, InformeFinanciero,InformeAcademico,Director, Contrato,AsisFinanza, AsisMatricula, CursoAlumno, Notificacion
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from datetime import date
from django.utils import timezone
from .forms import CalificacionForm, ObservacionForm, AlumnoForm, InformeFinancieroForm, ApoderadoForm, ContratoForm, AsistenciaForm
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
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

# ============================================================ MODULO INICIO ==============================================================================


def inicio(request):
    return render(request, 'inicio.html')

def quienes_somos(request):
    return render(request, 'quienes_somos.html')

# ============================================================ MODULO LOGIN ===============================================================================


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
                return redirect('alumno_dashboard')  # Redirigir al alumno

            # Verificar si es profesor
            elif hasattr(user, 'profesor'):
                login(request, user)
                return redirect('profesor')  # Redirigir al profesor

            # Verificar si es apoderado
            elif hasattr(user, 'apoderado'):
                login(request, user)
                return redirect('apoderado_view')  # Redirigir al apoderado

            # Verificar si es director
            elif hasattr(user, 'director'):
                login(request, user)
                return redirect('director_dashboard')  # Redirigir al director
            
            #Verificar si es asisfinanza
            elif hasattr(user, 'asisfinanza'):
                login(request, user)
                return redirect('panel_asisAdminFinan')  # Redirigir al asisfinanza
            
                #Verificar si es asisMatricula
            elif hasattr(user, 'asismatricula'):
                login(request, user)
                return redirect('panel_admision')  # Redirigir al asisMatricula
            
            # Otras redirecciones según roles adicionales
            else:
                login(request, user)
                return redirect('login')  # Redirigir a una página predeterminada si no es alumno, profesor, apoderado o director

        else:
            # Si las credenciales son inválidas
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'login.html')
# =================================================================== LOGOUT =============================================================
def logout_view(request):
    logout(request)
    return redirect('inicio') 


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

from django.utils.dateparse import parse_date

@login_required
def registrar_asistencia(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    profesor = curso.profesor

    # Obtener los alumnos aprobados
    alumnos_aprobados = CursoAlumno.objects.filter(curso=curso, alumno__estado_admision='Aprobado').select_related('alumno')

    success_message = None  # Inicializar el mensaje de éxito como None

    if request.method == 'POST':
        actividades_realizadas = request.POST.get('actividades_realizadas')
        observaciones = request.POST.get('observaciones')

        if not actividades_realizadas:
            success_message = "Debe registrar las actividades realizadas en la bitácora antes de guardar la asistencia."
        else:
            # Guardar bitácora
            BitacoraClase.objects.create(
                curso=curso,
                fecha=date.today(),
                profesor=profesor,
                actividades_realizadas=actividades_realizadas,
                observaciones=observaciones,
            )

            # Crear y guardar objeto Asistencia
            asistencia = Asistencia(curso=curso, fecha=date.today())
            asistencia.save()

            for curso_alumno in alumnos_aprobados:
                alumno = curso_alumno.alumno
                asistencia_estado = request.POST.get(f'asistencia_{alumno.id}')

                if asistencia_estado:
                    if asistencia_estado == 'presente':
                        asistencia.alumnos_presentes.add(alumno)
                    elif asistencia_estado == 'ausente':
                        asistencia.alumnos_ausentes.add(alumno)
                    elif asistencia_estado == 'justificado':
                        asistencia.alumnos_justificados.add(alumno)

            asistencia.save()
            success_message = "Bitácora y asistencia registradas exitosamente."  # Asignar el mensaje de éxito

    return render(request, 'registrarAsistencia.html', {
        'curso': curso,
        'alumnos_aprobados': alumnos_aprobados,
        'success_message': success_message,  # Pasar el mensaje de éxito al contexto
    })





@login_required
def historial_bitacoras(request, curso_id):
    # Obtener el curso y las bitácoras asociadas a este curso
    curso = get_object_or_404(Curso, id=curso_id)
    bitacoras = BitacoraClase.objects.filter(curso=curso).order_by('-fecha')  # Ordenadas por fecha descendente
    
    context = {
        'curso': curso,
        'bitacoras': bitacoras,
    }
    return render(request, 'historial_bitacoras.html', context)

@login_required
def eliminar_bitacora(request, bitacora_id):
    # Obtener la bitácora a través de su id, si no existe se muestra un error 404
    bitacora = get_object_or_404(BitacoraClase, id=bitacora_id)
    
    # Eliminar la bitácora
    bitacora.delete()
    
    # Mensaje de éxito
    messages.success(request, "Registro de bitácora eliminado exitosamente.")
    
    # Redireccionar de vuelta al historial de bitácoras
    return redirect(reverse('historial_bitacoras', kwargs={'curso_id': bitacora.curso.id}))

#=============================================================== REGISTRAR CALIFICACIONES ====================================================================


@login_required
def registrar_calificaciones(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    profesor = curso.profesor
    errores = {}
    form_list = {}
    success_message = None

    alumnos_aprobados = CursoAlumno.objects.filter(curso=curso, alumno__estado_admision='Aprobado').select_related('alumno')

    if request.method == 'POST':
        for curso_alumno in alumnos_aprobados:
            alumno = curso_alumno.alumno
            form = CalificacionForm(request.POST, prefix=str(alumno.id))
            if form.is_valid():
                calificacion, created = Calificacion.objects.get_or_create(
                    alumno=alumno,
                    curso=curso,
                    defaults={'nota': form.cleaned_data['nota']}
                )
                if not created:
                    calificacion.nota = form.cleaned_data['nota']
                    calificacion.save()
            else:
                errores[alumno] = form.errors

        if not errores:
            success_message = "Se han guardado los cambios exitosamente."

    else:
        form_list = {curso_alumno.alumno: CalificacionForm(prefix=str(curso_alumno.alumno.id)) for curso_alumno in alumnos_aprobados}

    return render(request, 'registrarCalificaciones.html', {
        'curso': curso,
        'form_list': form_list,
        'errores': errores,
        'success_message': success_message
    })



# =================================================== REGISTRO ACADEMICO =====================================================================================

@login_required
def registro_academico(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)

    # Filtrar solo alumnos aprobados a través de CursoAlumno
    curso_alumnos = CursoAlumno.objects.filter(curso=curso)
    alumnos_aprobados = [curso_alumno.alumno for curso_alumno in curso_alumnos]

    # Obtener calificaciones y asistencias para el curso
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
    
    # Obtén los CursoAlumno que correspondan al curso y filtren por estado de admisión 'Aprobado'
    curso_alumnos = CursoAlumno.objects.filter(curso=curso)
    alumnos_aprobados = Alumno.objects.filter(curso_alumno_relacion__in=curso_alumnos, estado_admision='Aprobado')

    return render(request, 'Profe_generar_informes.html', {'curso': curso, 'alumnos_aprobados': alumnos_aprobados})


# ============================================ generar informe en pdf para el profesor por alumno ================================================================
@login_required
def alumno_detalle(request, alumno_id):
    # Obtener el alumno
    alumno = get_object_or_404(Alumno, id=alumno_id)

    # Obtener el curso actual del alumno mediante el modelo CursoAlumno
    curso_alumno = CursoAlumno.objects.filter(alumno=alumno).first()
    curso_actual = curso_alumno.curso if curso_alumno else None

    # Si no se encuentra el curso, manejar el caso
    if not curso_actual:
        return render(request, 'alumno_detalle.html', {
            'alumno': alumno,
            'curso': None,
            'calificaciones': [],
            'asistencias': [],
            'ausencias': [],
            'justificaciones': [],
            'promedio': 0,
        })

    # Filtrar calificaciones del alumno por el curso actual
    calificaciones = Calificacion.objects.filter(alumno=alumno, curso=curso_actual)

    # Calcular el promedio de calificaciones
    promedio = calificaciones.aggregate(promedio=Avg('nota'))['promedio'] or 0

    # Filtrar asistencias, ausencias y justificaciones usando el curso actual
    asistencias = Asistencia.objects.filter(curso=curso_actual, alumnos_presentes=alumno)
    ausencias = Asistencia.objects.filter(curso=curso_actual, alumnos_ausentes=alumno)
    justificaciones = Asistencia.objects.filter(curso=curso_actual, alumnos_justificados=alumno)

    # Verificar si los datos de asistencia se obtienen correctamente (depuración)
    print("Asistencias:", asistencias)
    print("Ausencias:", ausencias)
    print("Justificaciones:", justificaciones)

    context = {
        'alumno': alumno,
        'curso': curso_actual,
        'calificaciones': calificaciones,
        'asistencias': asistencias,
        'ausencias': ausencias,
        'justificaciones': justificaciones,
        'promedio': promedio,
    }
    return render(request, 'alumno_detalle.html', context)

##============================================ generar pdf por alumno: asistencia y calificaciones================================

@login_required
def descargar_pdf_alumno(request, alumno_id):
    # Obtener el alumno específico o devolver 404 si no se encuentra
    alumno = get_object_or_404(Alumno, id=alumno_id)
    
    # Obtener las calificaciones y asistencias del alumno
    calificaciones = Calificacion.objects.filter(alumno=alumno)
    asistencias = Asistencia.objects.filter(alumnos_presentes=alumno)
    ausencias = Asistencia.objects.filter(alumnos_ausentes=alumno)
    justificaciones = Asistencia.objects.filter(alumnos_justificados=alumno)

    # Calcular el promedio de calificaciones
    if calificaciones:
        promedio = sum(calificacion.nota for calificacion in calificaciones) / len(calificaciones)
    else:
        promedio = 0

    # Preparar el contexto para la plantilla
    context = {
        'alumno': alumno,
        'calificaciones': calificaciones,
        'asistencias': asistencias,
        'ausencias': ausencias,
        'justificaciones': justificaciones,
        'promedio': promedio,
    }

    # Renderizar la plantilla HTML
    html_string = render_to_string('alumno_detalle.html', context)

    # Crear el objeto PDF
    html = HTML(string=html_string)

    # Preparar la respuesta HTTP para el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{alumno.nombre}_{alumno.apellido}_detalle.pdf"'

    # Generar el PDF y enviarlo en la respuesta
    html.write_pdf(response)

    return response

# =============================================================== OBSERVACIONES =========================================================================
@login_required
def observaciones(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    observaciones = Observacion.objects.filter(curso=curso)

    # Filtra solo los alumnos aprobados a través de CursoAlumno
    alumnos_aprobados = Alumno.objects.filter(curso_alumno_relacion__curso=curso, estado_admision='Aprobado')

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

    asistencias_data = []

    # Obtener los cursos en los que está inscrito el alumno a través de CursoAlumno
    cursos_alumno = CursoAlumno.objects.filter(alumno=alumno)

    for curso_alumno in cursos_alumno:
        curso = curso_alumno.curso  # Acceder al curso

        # Recuperar todas las fechas en las que el alumno estuvo presente, ausente o justificado para el curso
        fechas_presentes = set(Asistencia.objects.filter(curso=curso, alumnos_presentes=alumno).values_list('fecha', flat=True))
        fechas_ausentes = set(Asistencia.objects.filter(curso=curso, alumnos_ausentes=alumno).values_list('fecha', flat=True))
        fechas_justificados = set(Asistencia.objects.filter(curso=curso, alumnos_justificados=alumno).values_list('fecha', flat=True))

        # Combinar las fechas para obtener fechas únicas
        fechas_totales = fechas_presentes | fechas_ausentes | fechas_justificados
        total_clases = len(fechas_totales)  # Cuenta de fechas únicas

        # Calcular la asistencia
        total_asistencia = len(fechas_presentes) + len(fechas_justificados)
        porcentaje_asistencia = (total_asistencia / total_clases * 100) if total_clases > 0 else 0

        # Agregar datos al contexto
        asistencias_data.append({
            'curso': curso.nombre,
            'asignatura': curso.asignatura,
            'total_clases': total_clases,
            'asistencia': total_asistencia,
            'porcentaje_asistencia': round(porcentaje_asistencia, 2),
        })

    # Renderizar el template con los datos de asistencia
    return render(request, 'alumnoConsuAsis.html', {'asistencias_data': asistencias_data})




# =========================================================== Vista para la consulta de notas ==========================================================================

@login_required
def alumno_consulta_notas(request):
    # Obtener el alumno actual (suponiendo que el usuario esté autenticado)
    alumno = get_object_or_404(Alumno, user=request.user)

    # Obtener los cursos del alumno a través de CursoAlumno
    cursos_alumno = CursoAlumno.objects.filter(alumno=alumno)

    # Agregar el promedio de notas para cada curso
    cursos_con_promedios = []
    for curso_alumno in cursos_alumno:
        curso = curso_alumno.curso  # Acceder al curso
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
    apoderado = get_object_or_404(Apoderado, user=request.user)
    notificaciones_no_leidas = Notificacion.objects.filter(apoderado=apoderado, leida=False)

    context = {
        'notificaciones_no_leidas': notificaciones_no_leidas,
    }
    return render(request, 'apoderado.html', context)

def marcar_notificacion_como_leida(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, apoderado__user=request.user)
    notificacion.leida = True
    notificacion.save()
    return redirect('apoderado_view')

@login_required
def historial_notificaciones(request):
    apoderado = get_object_or_404(Apoderado, user=request.user)
    
    # Obtén todas las notificaciones del apoderado
    todas_notificaciones = Notificacion.objects.filter(apoderado=apoderado).order_by('-fecha_creacion')
    
    # Marcar como leídas todas las notificaciones no leídas
    notificaciones_no_leidas = todas_notificaciones.filter(leida=False)
    if notificaciones_no_leidas.exists():
        notificaciones_no_leidas.update(leida=True)

    return render(request, 'historial_notificaciones.html', {'notificaciones': todas_notificaciones})

#============================================================================= APODERADO ASISTENCIA =========================================================================================



@login_required
def apoderadoConsuAsis(request):
    # Obtiene el apoderado actual
    apoderado = get_object_or_404(Apoderado, user=request.user)
    
    # Obtiene los alumnos asociados al apoderado con estado de admisión "Aprobado"
    alumnos = Alumno.objects.filter(apoderado=apoderado, estado_admision='Aprobado')
    asistencias_data = {}

    for alumno in alumnos:
        # Obtiene los cursos asociados al alumno a través del modelo CursoAlumno
        cursos_asignados = CursoAlumno.objects.filter(alumno=alumno).select_related('curso')
        asistencias_data[alumno] = []

        for curso_alumno in cursos_asignados:
            curso = curso_alumno.curso  # Obtener el curso desde CursoAlumno
            # Recupera todas las fechas en las que el alumno estuvo en algún estado de asistencia para el curso
            fechas_presentes = set(Asistencia.objects.filter(curso=curso, alumnos_presentes=alumno).values_list('fecha', flat=True))
            fechas_ausentes = set(Asistencia.objects.filter(curso=curso, alumnos_ausentes=alumno).values_list('fecha', flat=True))
            fechas_justificados = set(Asistencia.objects.filter(curso=curso, alumnos_justificados=alumno).values_list('fecha', flat=True))

            # Combina las fechas para obtener fechas únicas
            fechas_totales = fechas_presentes | fechas_ausentes | fechas_justificados
            total_clases = len(fechas_totales)  # Cuenta de fechas únicas

            # Calcula la asistencia
            total_asistencia = len(fechas_presentes) + len(fechas_justificados)
            porcentaje_asistencia = (total_asistencia / total_clases * 100) if total_clases > 0 else 0

            asistencias_data[alumno].append({
                'curso': curso.nombre,  # Acceder al nombre del curso
                'total_clases': total_clases,
                'asistencia': total_asistencia,
                'porcentaje_asistencia': round(porcentaje_asistencia, 2),
            })

    context = {
        'alumnos': alumnos,
        'asistencias_data': asistencias_data,
    }
    return render(request, 'apoderadoConsuAsis.html', context)



# ============================================================================== APODERADO NOTAS ========================================================================================================

@login_required
def apoderadoConsuNotas(request):
    try:
        apoderado = Apoderado.objects.get(user=request.user)
    except Apoderado.DoesNotExist:
        return render(request, 'error.html', {'mensaje': 'No se encontró apoderado para este usuario.'})

    alumnos = Alumno.objects.filter(apoderado=apoderado, estado_admision="Aprobado")
    if not alumnos.exists():
        return render(request, 'error.html', {'mensaje': 'No se encontró un alumno asociado con este apoderado.'})

    # Estructura de datos para almacenar calificaciones organizadas
    alumnos_data = []

    for alumno in alumnos:
        alumno_info = {
            'alumno': alumno,
            'cursos': []
        }

        # Obtener los cursos asignados al alumno a través de CursoAlumno
        cursos_asignados = CursoAlumno.objects.filter(alumno=alumno).select_related('curso')
        
        for curso_alumno in cursos_asignados:
            curso = curso_alumno.curso  # Obtener el curso desde CursoAlumno
            
            # Obtener las calificaciones del alumno para el curso específico
            calificaciones_curso = Calificacion.objects.filter(alumno=alumno, curso=curso)
            # Calcular el promedio de notas
            total_notas = sum(c.nota for c in calificaciones_curso if c.nota is not None)
            count_notas = calificaciones_curso.count()
            promedio = round(total_notas / count_notas, 2) if count_notas > 0 else 0

            # Crear una lista numerada de calificaciones
            calificaciones_numeradas = [{'numero': i + 1, 'nota': calificacion.nota} for i, calificacion in enumerate(calificaciones_curso)]
            
            curso_info = {
                'curso': curso,
                'calificaciones': calificaciones_numeradas,
                'promedio': promedio
            }
            alumno_info['cursos'].append(curso_info)

        alumnos_data.append(alumno_info)

    # Pasar los datos al contexto para renderizar en la plantilla
    context = {
        'alumnos_data': alumnos_data,
    }
    return render(request, 'apoderadoConsuNotas.html', context)


# ======================================================================= APODERADO OBSERVACIONES ================================================================================================

@login_required
def apoderado_observaciones(request):
    # Obtiene el apoderado actual
    apoderado = get_object_or_404(Apoderado, user=request.user)
    
    # Obtiene los alumnos asociados al apoderado con estado de admisión aprobado
    alumnos_aprobados = Alumno.objects.filter(apoderado=apoderado, estado_admision="Aprobado")
    
    # Obtiene las observaciones asociadas a estos alumnos en sus respectivos cursos
    observaciones_data = []
    
    for alumno in alumnos_aprobados:
        # Obtener los cursos del alumno a través de CursoAlumno
        cursos_asignados = CursoAlumno.objects.filter(alumno=alumno).select_related('curso')
        
        for curso_alumno in cursos_asignados:
            curso = curso_alumno.curso  # Obtener el curso desde CursoAlumno
            
            # Obtener las observaciones del alumno para el curso específico
            observaciones_alumno = Observacion.objects.filter(alumno=alumno, curso=curso)
            
            # Almacenar los datos de observaciones en la lista
            observaciones_data.append({
                'alumno': alumno,
                'curso': curso,
                'observaciones': observaciones_alumno
            })

    context = {
        'observaciones_data': observaciones_data
    }

    return render(request, 'apoderadoObservaciones.html', context)


# ==================================================================== DIRECTOR =========================================================================================
@login_required
def director_dashboard(request):
    return render(request, 'director.html') 
@login_required
def directorMenu(request):
    # Aquí podrías agregar lógica para consultar informes si es necesario
    return render(request, 'directorMenu.html')

@csrf_exempt
def director_plani(request):
    cursos = Curso.objects.all()

    if request.method == "POST":
        # Procesar la edición del curso con JSON
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
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return render(request, 'directorPlani.html', {'cursos': cursos})

@login_required
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

import json
@csrf_exempt  # Solo si es necesario; no recomendado para producción sin protección
def update_curso(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            curso_id = data.get("curso_id")
            hora = data.get("hora")
            sala = data.get("sala")

            # Verifica que el curso existe
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

#pdf director
@login_required
def direcPdfInfoAca(request):
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

    # Crear el contexto para la plantilla PDF
    context = {
        'informes': informes
    }

    # Renderizar la plantilla en un string HTML
    html_string = render_to_string('direInfoAca_pdf.html', context)
    html = HTML(string=html_string)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_academico.pdf"'
    
    # Generar el PDF
    html.write_pdf(response)
    return response


#informe academico
@login_required
def direcPdfPlanificacion(request):
    # Obtener los cursos de la planificación académica
    cursos = Curso.objects.all()

    # Cargar la plantilla y renderizarla como HTML
    html_string = render_to_string('direcPdfPlanificacion_pdf.html', {'cursos': cursos})

    # Crear el PDF en un archivo temporal
    html = HTML(string=html_string)
    result = html.write_pdf()

    # Generar la respuesta HTTP con el archivo PDF
    response = HttpResponse(result, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="planificacion_academica.pdf"'

    return response


# ========================================================================= INFORME FINANCIERO ==========================================================================================
@login_required
def informe_financiero_view(request):
    datos = InformeFinanciero.objects.all()
    return render(request, 'informe_financiero.html', {'datos': datos})

@login_required
def informe_financiero_view(request):
    if request.method == 'POST':
        form = InformeFinancieroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('informe_financiero')  # Redirige después de agregar
    else:
        form = InformeFinancieroForm()
    
    # Obtener todos los informes financieros
    informes = InformeFinanciero.objects.all()


    context = {
        'form': form,
        'informes': informes,
    }
    return render(request, 'informe_financiero.html', context)

# ===================================================================================================================================================================================
@login_required
def generar_pdf_view(request):
    # Obtener todos los informes financieros del modelo
    informes = InformeFinanciero.objects.all()

    # Crear el contexto con los informes
    context = {
        'titulo': 'Informe Finanzas Primer Semestre',
        'informes': informes,
    }

    # Renderizar el template a un HTML
    html_string = render_to_string('pdf/informe_financiero_pdf.html', context)

    # Convertir el HTML a PDF
    pdf = HTML(string=html_string).write_pdf()

    # Crear una respuesta HTTP con el PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="informe_financiero.pdf"'
    return response


@login_required
def eliminar_informe_view(request, informe_id):
    informe = get_object_or_404(InformeFinanciero, id=informe_id)

    if request.method == 'POST':
        informe.delete()
        # Redirigir a la lista de informes después de eliminar
        return redirect('informe_financiero')

    return render(request, 'confirmar_eliminacion.html', {'informe': informe})
# ========================================================================== ADMISION Y MATRICULA ============================================================================================
@login_required
def gestionar_estudiantes(request):
    alumnos_pendientes = Alumno.objects.filter(estado_admision='Pendiente')
    alumnos_aprobados = Alumno.objects.filter(estado_admision='Aprobado')
    
    context = {
        'alumnos_pendientes': alumnos_pendientes,
        'alumnos_aprobados': alumnos_aprobados,
    }
    
    return render(request, 'gestionar_estudiantes.html', context)


@login_required
def agregar_alumno(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)

        # Verifica si el formulario es válido
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Verifica si el usuario ya existe
            if User.objects.filter(username=email).exists():
                form.add_error('email', 'Este correo electrónico ya está en uso.')
            else:
                try:
                    # Guarda el Alumno y las relaciones de CursoAlumno usando el método save del formulario
                    form.save()
                    return redirect('gestionar_estudiantes')  # Redirige a la página de gestión de estudiantes
                except IntegrityError:
                    form.add_error(None, 'Ocurrió un error al crear el usuario. Intenta nuevamente.')
                except Exception as e:
                    form.add_error(None, f'Ocurrió un error inesperado: {str(e)}')
        else:
            # Mostrar errores del formulario en caso de que no sea válido
            print(form.errors)

    else:
        form = AlumnoForm()  # Instancia un formulario vacío si no es un POST

    return render(request, 'agregar_alumno.html', {'form': form})  # Renderiza el formulario en la plantilla



@login_required
def eliminar_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    alumno.delete()  # Eliminar el alumno
    return redirect('gestionar_estudiantes')  # Redirige a la lista de estudiantes




@login_required
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


@login_required
def panel_admision(request):
    alumnos = Alumno.objects.all()  # Obtiene todos los alumnos
    return render(request, 'panel_admision.html', {'alumnos': alumnos})


# =================================================================== DASHBOARD DE ASISTENTE DE ADMISIÓN Y FINANZAS ==============================================================
@login_required
def asisAdminFinan_dashboard(request):
    return render(request, 'asisAdminFinan.html')  # Renderiza el dashboard del profesor

# =====================================================VISTA de ASISTENTE DE ADMISIÓN Y FINANZAS ==========================================
@login_required
def ver_gestion_pagos_admision(request):
    # Consulta de todos los alumnos
    alumnos = Alumno.objects.all()

    # Pasar los alumnos al contexto
    context = {
        'alumnos': alumnos
    }

    return render(request, 'asisAdmiFinan_gestion_pagos.html', context)

# =====================================================VISTA de ASISTENTE DE ADMISIÓN Y FINANZAS PARA AGREGAR ALUMNO ==========================================
@login_required
def agregar_alumno_asis(request):
    if request.method == 'POST':
        form = AlumnoForm(request.POST)
        if form.is_valid():
            # Primero crea el usuario
            user = User.objects.create_user(
                username=form.cleaned_data['email'],  
                password=form.cleaned_data['password'],  
                email=form.cleaned_data['email'],
            )
            # Luego crea el Alumno
            alumno = Alumno(
                user=user,
                nombre=form.cleaned_data['nombre'],
                apellido=form.cleaned_data['apellido'],
                email=form.cleaned_data['email'],
                apoderado=form.cleaned_data['apoderado'],  
                estado_admision=form.cleaned_data['estado_admision'],  
                curso=form.cleaned_data['curso'],  
            )
            alumno.save()  # Guarda el alumno en la base de datos
            return redirect('asisAdmiFinan_gestion_pagos')  # Redirige a la lista de estudiantes
    else:
        form = AlumnoForm()  # Si no es POST, crea un nuevo formulario
    
    return render(request, 'agregar_alumno_asis.html', {'form': form})  # Renderiza la plantilla con el formulario

# =====================================================VISTA de ASISTENTE DE ADMISIÓN Y FINANZAS PARA ELIMINAR ALUMNO =====================
@login_required
def eliminar_alumno_asis(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    alumno.delete()  # Eliminar el alumno
    return redirect('asisAdmiFinan_gestion_pagos')  # Redirige a la lista de estudiantes

# =====================================================VISTA de ASISTENTE DE ADMISIÓN Y FINANZAS PARA ACTUALIZAR INFORME=====================
@login_required
def editar_informe_asis(request, id):
    # Obtener el alumno por ID
    alumno_instance = get_object_or_404(Alumno, id=id)
    
    # Obtener el contrato relacionado con el alumno (si existe)
    contrato_instance = Contrato.objects.filter(alumno=alumno_instance).first()

    # Obtener el apoderado del alumno
    apoderado_instance = alumno_instance.apoderado  # Asegúrate de que el modelo Alumno tenga relación con Apoderado

    if request.method == 'POST':
        form = ContratoForm(request.POST, instance=contrato_instance, alumno_instance=alumno_instance, apoderado_instance=apoderado_instance)
        
        if form.is_valid():
            # Recuperar el apoderado por su ID del campo oculto
            apoderado_id = form.cleaned_data['apoderado_id']
            apoderado = Apoderado.objects.get(id=apoderado_id)

            # Asignar la instancia del apoderado al contrato
            contrato = form.save(commit=False)
            contrato.apoderado = apoderado
            contrato.alumno = alumno_instance
            contrato.save()

            # Redirigir a la URL de éxito
            return redirect('editar_informe_asis', id=alumno_instance.id)
    else:
        form = ContratoForm(instance=contrato_instance, alumno_instance=alumno_instance, apoderado_instance=apoderado_instance)

    return render(request, 'asis_edicion_info_pago.html', {'form': form, 'alumno': alumno_instance})
#==================================================  Generar contrato PDF =================================================================
@login_required
def generar_pdf_contrato(request, id):
    # Obtener el alumno y el contrato correspondiente
    alumno = get_object_or_404(Alumno, id=id)
    contrato = Contrato.objects.filter(alumno=alumno).first()

    # Verificar si el contrato existe
    if contrato is None:
        return HttpResponse("No se encontró el contrato asociado al alumno.", status=404)

    # Cargar la plantilla HTML
    context = {'alumno': alumno, 'contrato': contrato}
    html_string = render_to_string('pdf/asis_pago.html', context)

    # Crear el PDF
    pdf = HTML(string=html_string).write_pdf()

    # Crear la respuesta HTTP con el PDF
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="pago_{alumno.nombre}_{alumno.apellido}.pdf"'

    return response

#SUBDIRECTOR
def subdirector_home(request):
    return render(request, 'subdirector.html')

def consulta_informes_academicos(request):
    cursos = Curso.objects.all()  # Obtén todos los cursos de la base de datos
    return render(request, 'subdire_consulta_informes_academicos.html', {'cursos': cursos})

def gestion_recursos_academicos(request):
    cursos = Curso.objects.select_related('profesor').all()  # Trae todos los cursos y sus profesores asociados
    return render(request, 'gestion_recursos_academicos.html', {'cursos': cursos})


def detalle_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    estudiantes = curso.alumnos.all()  # Obtiene todos los alumnos del curso

    # Crear una lista de estudiantes con sus promedios de calificaciones
    estudiantes_con_promedio = []
    for estudiante in estudiantes:
        # Calcula el promedio de notas en las calificaciones asociadas al estudiante y curso
        promedio_calificaciones = Calificacion.objects.filter(
            alumno=estudiante,
            curso=curso
        ).aggregate(promedio=Avg('nota'))['promedio']

        # Redondea el promedio a 2 decimales si no es None
        promedio_redondeado = round(promedio_calificaciones, 2) if promedio_calificaciones is not None else "-"

        estudiantes_con_promedio.append({
            'nombre': estudiante.nombre,
            'apellido': estudiante.apellido,
            'promedio_notas': promedio_redondeado
        })

    return render(request, 'detalle_curso.html', {'curso': curso, 'estudiantes': estudiantes_con_promedio})

def detalle_curso_pdf(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    estudiantes = curso.alumnos.all()

    # Calcular el promedio de notas y preparar datos para el PDF
    estudiantes_con_promedio = []
    for estudiante in estudiantes:
        promedio_calificaciones = Calificacion.objects.filter(
            alumno=estudiante,
            curso=curso
        ).aggregate(promedio=Avg('nota'))['promedio']
        
        promedio_redondeado = round(promedio_calificaciones, 2) if promedio_calificaciones is not None else "-"
        
        estudiantes_con_promedio.append({
            'nombre': estudiante.nombre,
            'apellido': estudiante.apellido,
            'promedio_notas': promedio_redondeado
        })

    # Renderizar la plantilla HTML a un string
    html_string = render_to_string('detalle_curso_pdf.html', {'curso': curso, 'estudiantes': estudiantes_con_promedio})

    # Crear el PDF usando WeasyPrint
    pdf = HTML(string=html_string).write_pdf()

    # Enviar el PDF como respuesta HTTP
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{curso.nombre}_reporte.pdf"'
    return response

#SOSTENEDOR
def sostenedor(request):
    # Simplemente renderiza el template "sostenedor.html"
    return render(request, 'sostenedor.html')

def establecimientos(request):
    # Calcular los totales para "Colegio Nuevos Horizontes"
    total_salas = Curso.objects.count()  # Asumimos que cada curso representa una sala
    total_alumnos = Alumno.objects.count()
    total_cursos = Curso.objects.count()
    total_profesores = Profesor.objects.count()
    
    # Contar empleados en los modelos específicos
    total_directores = Director.objects.count()
    total_asistentes_matricula = AsisMatricula.objects.count()
    total_asistentes_finanza = AsisFinanza.objects.count()
    
    # Sumar el total de empleados (Director, Profesor, AsisMatricula, AsisFinanza)
    total_empleados = total_directores + total_profesores + total_asistentes_matricula + total_asistentes_finanza

    # Pasar los totales al template
    contexto = {
        'colegio_nombre': 'Colegio Nuevos Horizontes',
        'total_salas': total_salas,
        'total_alumnos': total_alumnos,
        'total_cursos': total_cursos,
        'total_profesores': total_profesores,
        'total_empleados': total_empleados
    }

    return render(request, 'establecimientos.html', contexto)







