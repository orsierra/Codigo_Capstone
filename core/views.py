# views.py
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Curso, BitacoraClase, Profesor,Asistencia, Calificacion, Informe, Observacion, Alumno, Apoderado, Curso, InformeFinanciero,InformeAcademico,Director, Contrato,AsisFinanza, AsisMatricula, CursoAlumno, Notificacion, Establecimiento,Subdirector
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404
from datetime import date
from django.utils import timezone
from .forms import CalificacionForm, ObservacionForm, AlumnoForm, InformeFinancieroForm, ApoderadoForm, ContratoForm, AsistenciaForm, CursoForm
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
from django.http import Http404, HttpResponseForbidden

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
                establecimiento_id = alumno.establecimiento_id  # Similar a cómo se hace con el profesor
                login(request, user)
                return redirect('alumno_dashboard',establecimiento_id=establecimiento_id)
    
            if hasattr(user, 'profesor'):
                profesor = user.profesor  #
                establecimiento_id = profesor.establecimiento_id 
                login(request, user)
                return redirect('profesor', establecimiento_id=establecimiento_id)  

            elif hasattr(user, 'apoderado'):
                apoderado = user.apoderado  
                establecimiento_id = apoderado.establecimiento_id  
                login(request, user)
                return redirect('apoderado_view', establecimiento_id=establecimiento_id) 
                
            elif hasattr(user, 'director'):
                director = user.director
                establecimiento_id = director.establecimiento_id
                login(request, user)
                return redirect('director_dashboard')
            
            elif hasattr(user, 'subdirector'):
                subdirector = user.subdirector
                establecimiento_id = subdirector.establecimiento_id 
                login(request, user)
                return redirect('subdirector_home')
            
            elif hasattr(user, 'sostenedor'):
                login(request, user)
                return redirect('sostenedor')

            elif hasattr(user, 'asisfinanza'):
                asisfinanza = user.asisfinanza  # Obtener el objeto profesor
                establecimiento_id = asisfinanza.establecimiento_id  # Asegúrate de que el modelo Profesor tenga un campo `establecimiento`
                login(request, user)
                return redirect('panel_asisAdminFinan', establecimiento_id=establecimiento_id)  # Pasa el establecimiento_id aquí
            
                #Verificar si es asisMatricula
            elif hasattr(user, 'asismatricula'):
                asismatricula = user.asismatricula
                establecimiento_id = asismatricula.establecimiento_id  # Asegúrate de que el modelo Profesor tenga un campo `establecimiento`
                login(request, user)
                return redirect('panel_admision', establecimiento_id=establecimiento_id)
            else:
                login(request, user)
                return redirect('login')

        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'login.html')

#==================================================================== Logout ==========================================================
def logout_view(request):
    logout(request)
    return redirect('inicio') 

# =====================================================================Dashboard de profesor ==========================================================
@login_required
def profesor_dashboard(request, establecimiento_id):
    # Verificar que el establecimiento_id no sea vacío o inválido
    if not establecimiento_id:
        raise Http404("Establecimiento no encontrado")
    
    # Obtener el establecimiento correspondiente
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    
    # Renderizar la plantilla con el establecimiento
    return render(request, 'profesor.html', {'establecimiento': establecimiento})

# =================================================================== profesor cursos =====================================================================
# Profesor - cursos 
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


# ====================================== LIBRO DE CLASES ===========================================================================
@login_required
def libro_clases(request, establecimiento_id, curso_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=establecimiento)

    # Obtener los alumnos del curso a través de la relación CursoAlumno
    curso_alumnos = CursoAlumno.objects.filter(curso=curso)
    alumnos = Alumno.objects.filter(id__in=curso_alumnos.values('alumno_id'))  # Filtra los alumnos según los cursos a los que están asignados

    context = {
        'curso': curso,
        'establecimiento': establecimiento,
        'alumnos': alumnos,
    }
    return render(request, 'profesorLibro.html', context)



# ============================================Registrar asistencia ================================================================

@login_required
def registrar_asistencia(request, establecimiento_id, curso_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=establecimiento)
    profesor = curso.profesor

    # Filtrar los alumnos aprobados para el curso y establecimiento específico
    alumnos_aprobados = CursoAlumno.objects.filter(
        curso=curso,
        alumno__estado_admision='Aprobado',
        alumno__establecimiento=establecimiento
    ).select_related('alumno')

    if not alumnos_aprobados.exists():
        messages.warning(request, f"No hay alumnos aprobados asociados al curso {curso.nombre}.")
        return redirect('profesor_cursos', establecimiento_id=establecimiento_id)

    success_message = None

    if request.method == 'POST':
        actividades_realizadas = request.POST.get('actividades_realizadas')
        observaciones = request.POST.get('observaciones')

        if not actividades_realizadas:
            messages.error(request, "Debe registrar las actividades realizadas en la bitácora antes de guardar la asistencia.")
        else:
            # Guardar en la bitácora de clase
            BitacoraClase.objects.create(
                curso=curso,
                fecha=timezone.now(),
                profesor=profesor,
                actividades_realizadas=actividades_realizadas,
                observaciones=observaciones,
            )

            # Crear registro de asistencia
            asistencia = Asistencia.objects.create(
                curso=curso,
                fecha=timezone.now(),
                establecimiento=establecimiento
            )

            # Registrar el estado de asistencia para cada alumno aprobado
            for alumno in alumnos_aprobados:
                alumno_instance = alumno.alumno
                estado = request.POST.get(f'asistencia_{alumno_instance.id}')
                
                if estado == 'presente':
                    asistencia.alumnos_presentes.add(alumno_instance)
                elif estado == 'ausente':
                    asistencia.alumnos_ausentes.add(alumno_instance)
                elif estado == 'justificado':
                    asistencia.alumnos_justificados.add(alumno_instance)

            success_message = "Bitácora y asistencia registradas exitosamente."

    return render(request, 'registrarAsistencia.html', {
        'curso': curso,
        'alumnos_aprobados': alumnos_aprobados,
        'establecimiento': establecimiento,
        'success_message': success_message,  # Enviar mensaje de éxito al template
    })

#========================================================== HISTORIAL BITÁCORA =============================================================


@login_required
def historial_bitacoras(request, establecimiento_id, curso_id):
    # Obtener el establecimiento y el curso
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=establecimiento)
    
    # Obtener las bitácoras asociadas al curso, ordenadas por fecha descendente
    bitacoras = BitacoraClase.objects.filter(curso=curso).order_by('-fecha')

    context = {
        'curso': curso,
        'establecimiento': establecimiento,
        'bitacoras': bitacoras,
    }
    
    return render(request, 'historial_bitacoras.html', context)


#=================================================== ELIMINAR BITACORA==============================================================


@login_required
def eliminar_bitacora(request, establecimiento_id, bitacora_id):
    # Obtener la bitácora a través de su id, si no existe se muestra un error 404
    bitacora = get_object_or_404(BitacoraClase, id=bitacora_id)
    
    # Obtener el establecimiento relacionado al curso
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    
    # Eliminar la bitácora
    bitacora.delete()
    
    # Mensaje de éxito
    messages.success(request, "Registro de bitácora eliminado exitosamente.")
    
    # Redireccionar de vuelta al historial de bitácoras con el establecimiento
    return redirect(reverse('historial_bitacoras', kwargs={'establecimiento_id': establecimiento.id, 'curso_id': bitacora.curso.id}))

#=============================================================== REGISTRAR CALIFICACIONES =======================================================================

@login_required
def registrar_calificaciones(request, establecimiento_id, curso_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=establecimiento)
    errores = {}
    form_list = {}
    success_message = None  # Variable para almacenar el mensaje de éxito

    # Filtrar alumnos aprobados para el curso y establecimiento específicos
    alumnos_aprobados = CursoAlumno.objects.filter(
        curso=curso, 
        alumno__estado_admision='Aprobado',
        alumno__establecimiento=establecimiento
    ).select_related('alumno')

    if request.method == 'POST':
        for curso_alumno in alumnos_aprobados:
            alumno = curso_alumno.alumno
            form = CalificacionForm(request.POST, prefix=str(alumno.id))
            if form.is_valid():
                # Crear una nueva calificación
                nota = form.cleaned_data['nota']
                Calificacion.objects.create(
                    alumno=alumno,
                    curso=curso,
                    establecimiento=curso.establecimiento,
                    nota=nota
                )
                
                # Verificar si la calificación es menor a 4 para crear la notificación
                if nota < 4:
                    apoderado = alumno.apoderado
                    if apoderado:
                        # Crear la notificación en la base de datos para el apoderado
                        mensaje = f"Su representado {alumno.nombre} {alumno.apellido} ha obtenido una calificación de {nota} en {curso.nombre}."
                        Notificacion.objects.create(
                            establecimiento=establecimiento,
                            apoderado=apoderado,
                            mensaje=mensaje,
                            tipo='calificacion_baja',
                            prioridad=1  # Asignar prioridad alta para calificaciones bajas
                        )
            else:
                errores[alumno] = form.errors

        # Verificar si no hubo errores en ningún formulario
        if not errores:
            success_message = "Se han guardado los cambios exitosamente."

    else:
        # Crear un formulario vacío para cada alumno aprobado
        form_list = {curso_alumno.alumno: CalificacionForm(prefix=str(curso_alumno.alumno.id)) for curso_alumno in alumnos_aprobados}

    return render(request, 'registrarCalificaciones.html', {
        'curso': curso,
        'form_list': form_list,
        'errores': errores,
        'success_message': success_message,  # Pasar el mensaje de éxito al contexto
        'establecimiento': establecimiento,
    })


# =================================================== REGISTRO ACADEMICO =====================================================================================

@login_required
def registro_academico(request, establecimiento_id, curso_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=establecimiento)

    # Filtrar solo alumnos aprobados en el curso y establecimiento especificados
    curso_alumnos = CursoAlumno.objects.filter(curso=curso, alumno__estado_admision='Aprobado', alumno__establecimiento=establecimiento)
    alumnos_aprobados = [curso_alumno.alumno for curso_alumno in curso_alumnos]

    # Obtener calificaciones y asistencias para el curso, filtradas por establecimiento
    calificaciones = Calificacion.objects.filter(curso=curso, establecimiento=establecimiento)
    asistencias = Asistencia.objects.filter(curso=curso)

    # Construir diccionarios para mapear alumnos con sus calificaciones, promedios y asistencias
    calificaciones_por_alumno = {}
    promedios_por_alumno = {}
    asistencias_por_alumno = {}

    for alumno in alumnos_aprobados:
        # Filtrar calificaciones por alumno
        calificaciones_alumno = calificaciones.filter(alumno=alumno)
        calificaciones_por_alumno[alumno] = calificaciones_alumno
        promedio = calificaciones_alumno.aggregate(Avg('nota'))['nota__avg'] or 0
        promedios_por_alumno[alumno] = round(promedio, 2)

        # Obtener asistencias del alumno sin duplicación (considerando presente, ausente o justificado)
        asistencias_alumno = asistencias.filter(
            Q(alumnos_presentes=alumno) |
            Q(alumnos_ausentes=alumno) |
            Q(alumnos_justificados=alumno)
        ).distinct()  # Agregamos distinct() para evitar duplicados
        asistencias_por_alumno[alumno] = asistencias_alumno

    context = {
        'curso': curso,
        'calificaciones_por_alumno': calificaciones_por_alumno,
        'promedios_por_alumno': promedios_por_alumno,
        'asistencias_por_alumno': asistencias_por_alumno,
        'establecimiento': establecimiento,
    }
    return render(request, 'registroAcademico.html', context)



# ===============================================================================================================================================================

@login_required
def generar_informes(request, establecimiento_id, curso_id):
    # Obtiene el establecimiento y el curso
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=establecimiento)

    # Obtener el profesor asociado al curso
    profesor = curso.profesor

    # Verifica que el profesor esté asociado al curso
    if not profesor:
        return HttpResponseForbidden("No se encontró un profesor asociado a este curso.")

    # Filtra los CursoAlumno que correspondan al curso y por estado de admisión 'Aprobado'
    curso_alumnos = CursoAlumno.objects.filter(curso=curso)
    alumnos_aprobados = Alumno.objects.filter(
        curso_alumno_relacion__in=curso_alumnos,
        estado_admision='Aprobado',
        establecimiento=establecimiento
    )

    return render(request, 'Profe_generar_informes.html', {
        'curso': curso,
        'alumnos_aprobados': alumnos_aprobados,
        'establecimiento': establecimiento,
        'profesor': profesor,  # Incluye el profesor en el contexto
    })



# ======================================================= Detalle de cada alumno del profesor ==================================================
@login_required
def alumno_detalle(request, establecimiento_id, curso_id, alumno_id):
    # Obtener el establecimiento usando el id de la URL
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    
    # Obtener el alumno usando su id y el establecimiento
    alumno = get_object_or_404(Alumno, id=alumno_id, establecimiento=establecimiento)
    
    # Obtener el curso usando el id de la URL
    curso = get_object_or_404(Curso, id=curso_id)

    # Verificar si el alumno está matriculado en el curso
    curso_alumno = CursoAlumno.objects.filter(alumno=alumno, curso=curso).first()
    if not curso_alumno:
        return HttpResponseForbidden("El alumno no está matriculado en este curso.")

    # Aquí puedes agregar lógica para obtener calificaciones, asistencias, etc.
    # Ejemplo:
    calificaciones = Calificacion.objects.filter(alumno=alumno, curso=curso)
    promedio = calificaciones.aggregate(promedio=Avg('nota'))['promedio'] or 0
        
    asistencias = Asistencia.objects.filter(curso=curso, alumnos_presentes=alumno)
    ausencias = Asistencia.objects.filter(curso=curso, alumnos_ausentes=alumno)
    justificaciones = Asistencia.objects.filter(curso=curso, alumnos_justificados=alumno)

    
    observaciones = Observacion.objects.filter(alumno=alumno, curso=curso) if curso else []
    # Otros datos para la plantilla
    context = {
        'establecimiento': establecimiento,
        'curso': curso,
        'alumno': alumno,
        'calificaciones': calificaciones,
        'promedio': promedio,
        'asistencias': asistencias,
        'ausencias': ausencias,
        'justificaciones': justificaciones,
        'observaciones': observaciones,
    }
    return render(request, 'alumno_detalle.html', context)


##============================================ generar pdf por alumno: asistencia y calificaciones================================


# Descargar PDF de alumno
@login_required
def descargar_pdf_alumno(request, establecimiento_id,curso_id, alumno_id):
    # Obtener el establecimiento usando el id de la URL
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    
    # Obtener el alumno usando su id y el establecimiento
    alumno = get_object_or_404(Alumno, id=alumno_id, establecimiento=establecimiento)
    
    # Obtener el curso usando el id de la URL
    curso = get_object_or_404(Curso, id=curso_id)

    # Verificar si el alumno está matriculado en el curso
    curso_alumno = CursoAlumno.objects.filter(alumno=alumno, curso=curso).first()
    if not curso_alumno:
        return HttpResponseForbidden("El alumno no está matriculado en este curso.")

    # Aquí puedes agregar lógica para obtener calificaciones, asistencias, etc.
    # Ejemplo:
    calificaciones = Calificacion.objects.filter(alumno=alumno, curso=curso)
    promedio = calificaciones.aggregate(promedio=Avg('nota'))['promedio'] or 0
    asistencias = Asistencia.objects.filter(curso=curso, alumnos_presentes=alumno)
    ausencias = Asistencia.objects.filter(curso=curso, alumnos_ausentes=alumno)
    justificaciones = Asistencia.objects.filter(curso=curso, alumnos_justificados=alumno)    
    observaciones = Observacion.objects.filter(alumno=alumno, curso=curso) if curso else []
    # Otros datos para la plantilla
    context = {
        'establecimiento': establecimiento,
        'curso': curso,
        'alumno': alumno,
        'calificaciones': calificaciones,
        'promedio': promedio,
        'asistencias': asistencias,
        'ausencias': ausencias,
        'justificaciones': justificaciones,
        'observaciones': observaciones,
    }

    html_string = render_to_string('alumno_detalle.html', context)
    html = HTML(string=html_string)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{alumno.nombre}_{alumno.apellido}_detalle.pdf"'
    html.write_pdf(response)

    return response

# =============================================================== OBSERVACIONES =========================================================================

@login_required
def observaciones(request, establecimiento_id, curso_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=establecimiento)
    observaciones = Observacion.objects.filter(curso=curso)

    alumnos_aprobados = CursoAlumno.objects.filter(
        curso=curso,
        alumno__estado_admision='Aprobado', 
        curso__establecimiento=establecimiento
    ).select_related('alumno')

    if not alumnos_aprobados.exists():
        messages.warning(request, f"No hay alumnos aprobados asociados al curso {curso.nombre}.")
        return redirect('profesor_cursos', establecimiento_id=establecimiento_id)

    if request.method == 'POST':
        if 'eliminar' in request.POST:
            observacion_id = request.POST.get('observacion_id')
            observacion = get_object_or_404(Observacion, id=observacion_id)
            observacion.delete()
            messages.success(request, "Observación eliminada exitosamente.")
            return redirect('observaciones', establecimiento_id=establecimiento.id, curso_id=curso.id)

        form = ObservacionForm(request.POST)
        form.fields['alumno'].queryset = Alumno.objects.filter(id__in=alumnos_aprobados.values_list('alumno', flat=True), establecimiento=establecimiento)
        if form.is_valid():
            observacion = form.save(commit=False)
            observacion.curso = curso
            observacion.save()
            messages.success(request, "Observación registrada exitosamente.")
            return redirect('observaciones', establecimiento_id=establecimiento.id, curso_id=curso.id)

    else:
        form = ObservacionForm()
        form.fields['alumno'].queryset = Alumno.objects.filter(id__in=alumnos_aprobados.values_list('alumno', flat=True), establecimiento=establecimiento)

    return render(request, 'observaciones.html', {
        'establecimiento': establecimiento,
        'curso': curso,
        'observaciones': observaciones,
        'form': form,
    })

# ============================================================= Dashboard de Alumno ==================================================

@login_required
def alumno_dashboard(request, establecimiento_id):
    # Opcional: Obtener el establecimiento del alumno si necesitas datos adicionales
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    context = {
        'establecimiento': establecimiento,
        # Agrega otros datos necesarios para el template
    }
    return render(request, 'alumno.html', context)


# ===================================================== Consulta de Asistencia del Alumno ============================================
@login_required
def alumno_consulta_asistencia(request, establecimiento_id):
    # Obtener el objeto Alumno asociado al usuario actual
    alumno = get_object_or_404(Alumno, user=request.user)

    # Obtener el establecimiento por el ID pasado como parámetro y validar que sea el mismo del alumno
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    if alumno.establecimiento != establecimiento:
        messages.error(request, 'No tiene permiso para consultar asistencias en este establecimiento.')
        return redirect('alumno_home')

    # Verificar el estado de admisión del alumno
    if alumno.estado_admision != 'Aprobado':
        messages.error(request, 'Su estado de admisión no le permite acceder a la consulta de asistencia.')
        return redirect('alumno_home')

    asistencias_data = []

    # Obtener los cursos en los que está inscrito el alumno en el establecimiento especificado
    cursos_alumno = CursoAlumno.objects.filter(alumno=alumno, curso__establecimiento=establecimiento)

    for curso_alumno in cursos_alumno:
        curso = curso_alumno.curso  # Acceder al curso

        # Obtener todos los IDs únicos de asistencias para el curso
        total_clases_ids = Asistencia.objects.filter(curso=curso).values_list('id', flat=True)
        total_clases = len(set(total_clases_ids))  # Contar IDs únicos

        # Obtener los IDs únicos de asistencias presentes
        asistencias_presentes_ids = Asistencia.objects.filter(curso=curso, alumnos_presentes=alumno).values_list('id', flat=True)
        asistencias_presentes = len(set(asistencias_presentes_ids))

        # Obtener los IDs únicos de asistencias justificadas
        asistencias_justificadas_ids = Asistencia.objects.filter(curso=curso, alumnos_justificados=alumno).values_list('id', flat=True)
        asistencias_justificadas = len(set(asistencias_justificadas_ids))

        # Calcular el total de asistencias (presente + justificado)
        total_asistencia = asistencias_presentes + asistencias_justificadas

        # Calcular el porcentaje de asistencia
        porcentaje_asistencia = (total_asistencia / total_clases * 100) if total_clases > 0 else 0

        # Agregar los datos al diccionario
        asistencias_data.append({
            'curso': curso.nombre,
            'asignatura': curso.asignatura,
            'total_clases': total_clases,
            'asistencia': total_asistencia,
            'porcentaje_asistencia': round(porcentaje_asistencia, 2),
        })

    return render(request, 'alumnoConsuAsis.html', {
        'asistencias_data': asistencias_data,
        'establecimiento': establecimiento,
    })



# =========================================================== Consulta de Notas del Alumno ============================================================

@login_required
def alumno_consulta_notas(request, establecimiento_id):
    # Obtener el objeto Alumno asociado al usuario actual
    alumno = get_object_or_404(Alumno, user=request.user)

    # Verificar que el alumno pertenece al establecimiento dado
    if alumno.establecimiento.id != establecimiento_id:
        # Redirige o lanza un error si el alumno no pertenece al establecimiento
        return render(request, 'error.html', {'mensaje': 'El alumno no pertenece a este establecimiento.'})

    # Obtener los cursos del alumno en el establecimiento actual
    cursos_alumno = CursoAlumno.objects.filter(
        alumno=alumno,
        curso__establecimiento_id=establecimiento_id  # Filtrar por establecimiento
    ).select_related('curso').prefetch_related('curso__calificacion_set')

    cursos_con_promedios = []

    # Iterar sobre los cursos en los que está inscrito el alumno
    for curso_alumno in cursos_alumno:
        curso = curso_alumno.curso  # Acceder al curso

        # Filtrar las calificaciones del alumno en el curso actual
        calificaciones = Calificacion.objects.filter(curso=curso, alumno=alumno)
        promedio = calificaciones.aggregate(average_nota=models.Avg('nota'))['average_nota'] if calificaciones.exists() else None

        # Agregar los datos del curso, calificaciones y promedio a la lista
        cursos_con_promedios.append({
            'curso': curso,
            'calificaciones': calificaciones,
            'promedio': round(promedio, 2) if promedio is not None else None
        })

    return render(request, 'alumnoConsuNotas.html', {
        'cursos_con_promedios': cursos_con_promedios,
        'establecimiento_id': establecimiento_id
    })


# ===================================================================== Vista del Apoderado ==================================================================

@login_required
def apoderado_view(request, establecimiento_id):  # Recibimos 'establecimiento_id' como parámetro
    # Obtener el objeto Apoderado asociado al usuario actual
    apoderado = get_object_or_404(Apoderado, user=request.user)

    # Asegurarse de que el establecimiento_id corresponda con el del apoderado
    if establecimiento_id != apoderado.establecimiento_id:
        return redirect('error_view')  # Redirigir a una página de error si los IDs no coinciden

    # Obtener las notificaciones no leídas para este apoderado y su establecimiento
    notificaciones_no_leidas = Notificacion.objects.filter(apoderado=apoderado, leida=False)

    context = {
        'notificaciones_no_leidas': notificaciones_no_leidas,
        'establecimiento_id': establecimiento_id,  # Pasar el establecimiento_id al contexto
    }

    return render(request, 'apoderado.html', context)


#=========================================== APODERADO NOTIFICACIONES ======================================================================
@login_required
def marcar_notificacion_como_leida(request, establecimiento_id, notificacion_id):
    # Obtener la notificación asociada al apoderado actual y al ID de la notificación
    notificacion = get_object_or_404(Notificacion, id=notificacion_id, apoderado__user=request.user)

    # Marcar la notificación como leída
    notificacion.leida = True
    notificacion.save()

    # Redirigir a la vista de apoderado con el establecimiento_id como argumento
    return redirect('apoderado_view', establecimiento_id=establecimiento_id)

#================================================== HISTORIAL NOTFICACIONES ===============================================================
@login_required
def historial_notificaciones(request, establecimiento_id):
    # Obtener el establecimiento desde la URL usando el parámetro 'establecimiento_id'
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    
    # Obtener el apoderado actual
    apoderado = get_object_or_404(Apoderado, user=request.user)
    
    # Aquí no es necesario actualizar 'establecimiento_id', ya que ya lo tienes con el parámetro 'establecimiento_id'
    
    # Obtener todas las notificaciones del apoderado, ordenadas por fecha de creación
    todas_notificaciones = Notificacion.objects.filter(apoderado=apoderado).order_by('-fecha_creacion')
    
    # Marcar como leídas todas las notificaciones no leídas
    notificaciones_no_leidas = todas_notificaciones.filter(leida=False)
    if notificaciones_no_leidas.exists():
        notificaciones_no_leidas.update(leida=True)

    # Pasar las notificaciones y el establecimiento al contexto
    return render(request, 'historial_notificaciones.html', {
        'notificaciones': todas_notificaciones,
        'establecimiento': establecimiento  # Pasar el objeto establecimiento completo al contexto
    })


#============================================================================= Consulta de Asistencia del Apoderado =========================================================================================
@login_required
def apoderadoConsuAsis(request, establecimiento_id):
    # Obtener el apoderado y el establecimiento
    apoderado = get_object_or_404(Apoderado, user=request.user)
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)

    # Verificar que el apoderado esté asociado al establecimiento
    if apoderado.establecimiento != establecimiento:
        return redirect('error_page')

    # Obtener los alumnos aprobados del apoderado
    alumnos = Alumno.objects.filter(apoderado=apoderado, estado_admision='Aprobado')
    asistencias_data = {}

    for alumno in alumnos:
        # Obtener cursos únicos en el establecimiento actual asignados al alumno
        cursos_asignados = Curso.objects.filter(curso_alumno_relacion__alumno=alumno, establecimiento=establecimiento).distinct()

        asistencias_data[alumno] = []

        for curso in cursos_asignados:
            # Obtener IDs únicos de asistencias por estado
            total_clases_ids = Asistencia.objects.filter(curso=curso).values_list('id', flat=True)
            total_clases = len(set(total_clases_ids))  # Total de clases (IDs únicos)

            asistencias_presentes_ids = Asistencia.objects.filter(curso=curso, alumnos_presentes=alumno).values_list('id', flat=True)
            asistencias_presentes = len(set(asistencias_presentes_ids))  # IDs únicos de asistencias presentes

            asistencias_justificadas_ids = Asistencia.objects.filter(curso=curso, alumnos_justificados=alumno).values_list('id', flat=True)
            asistencias_justificadas = len(set(asistencias_justificadas_ids))  # IDs únicos de asistencias justificadas

            # Calcular el total de asistencias (presente + justificado)
            total_asistencia = asistencias_presentes + asistencias_justificadas

            # Calcular el porcentaje de asistencia
            porcentaje_asistencia = (total_asistencia / total_clases * 100) if total_clases > 0 else 0

            # Agregar los datos al diccionario
            asistencias_data[alumno].append({
                'curso': curso.nombre,
                'total_clases': total_clases,
                'asistencia': total_asistencia,
                'porcentaje_asistencia': round(porcentaje_asistencia, 2),
            })

    context = {
        'alumnos': alumnos,
        'asistencias_data': asistencias_data,
        'establecimiento_id': establecimiento.id,
    }
    return render(request, 'apoderadoConsuAsis.html', context)



# ============================================================================== Consulta de Notas del Apoderado ============================================================================
@login_required
def apoderadoConsuNotas(request, establecimiento_id):
    # Obtener el apoderado y el establecimiento
    apoderado = get_object_or_404(Apoderado, user=request.user)
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)

    # Verificar que el apoderado esté asociado al establecimiento
    if apoderado.establecimiento != establecimiento:
        return redirect('error_page')
 
    # Obtener los alumnos aprobados del apoderado
    alumnos = Alumno.objects.filter(apoderado=apoderado, estado_admision="Aprobado")

    alumnos_data = []

    for alumno in alumnos:
        # Obtener los cursos únicos del alumno en el establecimiento específico
        cursos_alumno = CursoAlumno.objects.filter(
            alumno=alumno,
            curso__establecimiento=establecimiento
        ).select_related('curso').prefetch_related('curso__calificacion_set')

        cursos_con_promedios = []

        for curso_alumno in cursos_alumno:
            curso = curso_alumno.curso

            # Filtrar las calificaciones del alumno para este curso
            calificaciones = Calificacion.objects.filter(alumno=alumno, curso=curso)
            promedio = calificaciones.aggregate(average_nota=Avg('nota'))['average_nota'] if calificaciones.exists() else None

            # Agregar el curso, calificaciones y promedio a la lista de cursos
            cursos_con_promedios.append({
                'curso': curso,
                'calificaciones': calificaciones,
                'promedio': round(promedio, 2) if promedio is not None else None
            })

        # Agregar los datos del alumno y sus cursos al contexto
        alumnos_data.append({
            'alumno': alumno,
            'cursos': cursos_con_promedios
        })

    context = {
        'alumnos_data': alumnos_data,
        'establecimiento': establecimiento,
    }

    return render(request, 'apoderadoConsuNotas.html', context)
# ======================================================================= APODERADO OBSERVACIONES ================================================================================================

@login_required
def apoderado_observaciones(request, establecimiento_id):
    # Obtener el apoderado y el establecimiento
    apoderado = get_object_or_404(Apoderado, user=request.user)
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)

    # Verificar que el apoderado esté asociado al establecimiento
    if apoderado.establecimiento != establecimiento:
        return redirect('error_page')

    # Obtener los alumnos aprobados del apoderado
    alumnos_aprobados = Alumno.objects.filter(apoderado=apoderado, estado_admision="Aprobado")
    
    observaciones_data = []

    for alumno in alumnos_aprobados:
        # Obtener cursos únicos del alumno para el establecimiento actual
        cursos_asignados = Curso.objects.filter(curso_alumno_relacion__alumno=alumno, establecimiento=establecimiento).distinct()

        for curso in cursos_asignados:
            # Obtener observaciones únicas del alumno para el curso específico
            observaciones_alumno = Observacion.objects.filter(alumno=alumno, curso=curso)

            # Agregar datos de observaciones de cada curso a la lista
            observaciones_data.append({
                'alumno': alumno,
                'curso': curso,
                'observaciones': observaciones_alumno
            })

    # Pasar el establecimiento al contexto
    return render(request, 'apoderadoObservaciones.html', {
        'observaciones_data': observaciones_data,
        'establecimiento': establecimiento,
    })


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
        # Filtra los alumnos del curso que están en el establecimiento correcto
        alumnos = Alumno.objects.filter(curso_alumno_relacion__curso=curso, establecimiento=director.establecimiento).distinct()
        total_alumnos = alumnos.count()
        
        # Calcular el promedio de notas específico para el curso actual
        promedio_notas = Calificacion.objects.filter(alumno__in=alumnos, curso=curso).aggregate(Avg('nota'))['nota__avg'] or 0
        
        # Contabiliza los registros de asistencia específicos para el curso actual
        total_asistencias = Asistencia.objects.filter(curso=curso, alumnos_presentes__in=alumnos).count()
        total_ausentes = Asistencia.objects.filter(curso=curso, alumnos_ausentes__in=alumnos).count()
        total_justificados = Asistencia.objects.filter(curso=curso, alumnos_justificados__in=alumnos).count()
        total_dias = Asistencia.objects.filter(curso=curso).count()
        
        # Total de registros de asistencia considerados
        total_registros_asistencia = total_asistencias + total_ausentes + total_justificados

        # Calcular el porcentaje de asistencia en base a los registros totales
        promedio_asistencia = 0
        if total_alumnos > 0 and total_dias > 0:
            # Calcula el porcentaje en función de los presentes
            promedio_asistencia = (total_asistencias / total_registros_asistencia * 100) if total_registros_asistencia > 0 else 0

        # Limitar el valor máximo a 100% y redondear a un decimal
        promedio_asistencia = min(round(promedio_asistencia, 1), 100)

        informes.append({
            'curso': curso,
            'total_alumnos': total_alumnos,
            'promedio_notas': round(promedio_notas, 1) if promedio_notas > 0 else 'Sin notas',
            'promedio_asistencia': promedio_asistencia
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
        # Filtra los alumnos del curso en el establecimiento del director
        alumnos = Alumno.objects.filter(curso_alumno_relacion__curso=curso, establecimiento=director.establecimiento).distinct()
        total_alumnos = alumnos.count()
        
        # Calcular el promedio de notas específico para el curso actual
        promedio_notas = Calificacion.objects.filter(alumno__in=alumnos, curso=curso).aggregate(Avg('nota'))['nota__avg'] or 0
        
        # Contabiliza los registros de asistencia específicos para el curso actual
        total_asistencias = Asistencia.objects.filter(curso=curso, alumnos_presentes__in=alumnos).count()
        total_ausentes = Asistencia.objects.filter(curso=curso, alumnos_ausentes__in=alumnos).count()
        total_justificados = Asistencia.objects.filter(curso=curso, alumnos_justificados__in=alumnos).count()
        total_dias = Asistencia.objects.filter(curso=curso).count()
        
        # Total de registros de asistencia considerados
        total_registros_asistencia = total_asistencias + total_ausentes + total_justificados

        # Calcular el porcentaje de asistencia en base a los registros totales
        promedio_asistencia = 0
        if total_alumnos > 0 and total_dias > 0:
            promedio_asistencia = (total_asistencias / total_registros_asistencia * 100) if total_registros_asistencia > 0 else 0

        # Limitar el valor máximo a 100% y redondear a un decimal
        promedio_asistencia = min(round(promedio_asistencia, 1), 100)

        informes.append({
            'curso': curso,
            'total_alumnos': total_alumnos,
            'promedio_notas': round(promedio_notas, 1) if promedio_notas > 0 else 'Sin notas',
            'promedio_asistencia': promedio_asistencia
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
def gestionar_estudiantes(request, establecimiento_id):
    # Obtener el establecimiento por su ID
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)

    # Filtrar alumnos por estado de admisión y por establecimiento
    alumnos_pendientes = Alumno.objects.filter(estado_admision='Pendiente', establecimiento=establecimiento)
    alumnos_aprobados = Alumno.objects.filter(estado_admision='Aprobado', establecimiento=establecimiento)
    
    # Renderizar la plantilla con los alumnos filtrados y el establecimiento
    return render(request, 'gestionar_estudiantes.html', {
        'alumnos_pendientes': alumnos_pendientes,
        'alumnos_aprobados': alumnos_aprobados,
        'establecimiento': establecimiento
    })


# =================================================== Admisión - Agregar Alumno ===================================================
@login_required
def agregar_alumno(request, establecimiento_id):
    # Obtener el establecimiento por su ID
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)

    if request.method == 'POST':
        form = AlumnoForm(request.POST, establecimiento_instance=establecimiento)

        if form.is_valid():
            try:
                # Guardar el alumno
                form.save()
                return redirect('gestionar_estudiantes', establecimiento_id=establecimiento.id)
            except IntegrityError:
                form.add_error(None, 'Ocurrió un error al crear el usuario. Intenta nuevamente.')
            except Exception as e:
                form.add_error(None, f'Ocurrió un error inesperado: {str(e)}')
    else:
        form = AlumnoForm(establecimiento_instance=establecimiento)

    return render(request, 'agregar_alumno.html', {'form': form, 'establecimiento': establecimiento})


   
    
# =================================================== Admisión - Eliminar Alumno ===================================================
@login_required
def eliminar_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)

    # Verificar si el alumno pertenece al establecimiento del usuario actual
    try:
        asistente_matricula = AsisMatricula.objects.get(user=request.user)
    except AsisMatricula.DoesNotExist:
        messages.error(request, 'No existe un AsisMatricula asociado a este usuario.')
        return redirect('gestionar_estudiantes', establecimiento_id=alumno.establecimiento.id)  # Pasa el ID aquí
    
    if alumno.establecimiento == asistente_matricula.establecimiento:
        alumno.delete()
        messages.success(request, 'Alumno eliminado con éxito.')
    else:
        messages.error(request, 'No tienes permiso para eliminar este alumno.')
    
    return redirect('gestionar_estudiantes', establecimiento_id=alumno.establecimiento.id)  # Pasa el ID aquí


# =================================================== Admisión - Actualizar Matrícula ===================================================
@login_required
def actualizar_matricula(request, id):
    alumno = get_object_or_404(Alumno, id=id)

    # Verificar si el alumno pertenece al establecimiento del usuario actual
    try:
        asistente_matricula = AsisMatricula.objects.get(user=request.user)
    except AsisMatricula.DoesNotExist:
        messages.error(request, 'No existe un AsisMatricula asociado a este usuario.')
        return redirect('gestionar_estudiantes', establecimiento_id=alumno.establecimiento.id)  # Pasa el ID aquí
    
    if alumno.establecimiento != asistente_matricula.establecimiento:
        messages.error(request, 'No tienes permiso para actualizar este alumno.')
        return redirect('gestionar_estudiantes', establecimiento_id=alumno.establecimiento.id)  # Pasa el ID aquí

    if request.method == 'POST':
        # Pasamos el establecimiento actual al formulario
        form = AlumnoForm(request.POST, instance=alumno, establecimiento_instance=alumno.establecimiento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Matrícula actualizada con éxito.')
            return redirect('gestionar_estudiantes', establecimiento_id=alumno.establecimiento.id)  # Pasa el ID aquí
    else:
        # Al cargar el formulario, pasamos el establecimiento actual
        form = AlumnoForm(instance=alumno, establecimiento_instance=alumno.establecimiento)

    return render(request, 'actualizar_matricula.html', {
        'form': form,
        'alumno': alumno,
        'establecimiento': alumno.establecimiento  # Asegúrate de pasar esto
    })




# =================================================== Panel de Admisión ===================================================
@login_required
def panel_admision(request, establecimiento_id):
    # Obtener el establecimiento usando el ID pasado en la URL
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    
    # Verificar si el usuario tiene acceso a este establecimiento
    try:
        asistente_matricula = AsisMatricula.objects.get(user=request.user, establecimiento=establecimiento)
    except AsisMatricula.DoesNotExist:
        messages.error(request, 'No existe un AsisMatricula asociado a este usuario para este establecimiento.')
        return redirect('gestionar_estudiantes')
    
    # Filtrar los alumnos que pertenecen al establecimiento del usuario
    alumnos = Alumno.objects.filter(establecimiento=establecimiento)
    
    return render(request, 'panel_admision.html', {'alumnos': alumnos, 'establecimiento': establecimiento})

# =================================================== Asistente de Admisión y Finanzas - Dashboard ===================================================
@login_required
def asisAdminFinan_dashboard(request, establecimiento_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)  # Obtén el establecimiento si necesitas usarlo en el contexto
    return render(request, 'asisAdminFinan.html', {'establecimiento': establecimiento})  # Renderiza el dashboard con el establecimiento



# =================================================== Asistente de Admisión y Finanzas - Gestión de Pagos ===================================================
@login_required
def ver_gestion_pagos_admision(request, establecimiento_id):
    # Obtener el establecimiento usando el id proporcionado
    establecimiento = Establecimiento.objects.get(id=establecimiento_id)
    
    # Filtrar los alumnos relacionados con el establecimiento
    alumnos = Alumno.objects.filter(establecimiento=establecimiento)

    # Pasar tanto los alumnos como el establecimiento_id en el contexto
    context = {
        'alumnos': alumnos,
        'establecimiento_id': establecimiento.id,  # Pasamos el ID correctamente
    }

    return render(request, 'asisAdmiFinan_gestion_pagos.html', context)



# ===================================================== VISTA de ASISTENTE DE ADMISIÓN Y FINANZAS PARA AGREGAR ALUMNO ==========================================
@login_required
def agregar_alumno_asis(request, establecimiento_id):
    # Obtener el establecimiento por su ID
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)

    if request.method == 'POST':
        form = AlumnoForm(request.POST, establecimiento_instance=establecimiento)

        if form.is_valid():
            try:
                # Guardar el alumno, incluyendo el establecimiento y los cursos seleccionados
                form.save()
                return redirect('asisAdmiFinan_gestion_pagos', establecimiento_id=establecimiento.id)
            except IntegrityError:
                form.add_error(None, 'Ocurrió un error al crear el usuario. Intenta nuevamente.')
            except Exception as e:
                form.add_error(None, f'Ocurrió un error inesperado: {str(e)}')
    else:
        form = AlumnoForm(establecimiento_instance=establecimiento)

    return render(request, 'agregar_alumno_asis.html', {'form': form, 'establecimiento': establecimiento})






# =================================================== Asistente de Admisión y Finanzas - Eliminar Alumno ===================================================
@login_required
def eliminar_alumno_asis(request, establecimiento_id, alumno_id):
    alumno = get_object_or_404(Alumno, id=alumno_id)
    alumno.delete()  # Eliminar el alumno

    # Redirige a la lista de estudiantes del establecimiento específico
    return redirect('asisAdmiFinan_gestion_pagos', establecimiento_id=establecimiento_id)



# =================================================== Asistente de Admisión y Finanzas - Editar Informe ===================================================
@login_required
def editar_informe_asis(request, establecimiento_id, id):
    # Obtener el establecimiento por su ID
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)

    # Obtener el alumno por su ID
    alumno = get_object_or_404(Alumno, id=id)
    alumno_instance = get_object_or_404(Alumno, id=id)

    # Obtener el contrato relacionado con el alumno (si existe)
    contrato = Contrato.objects.filter(alumno=alumno).first()
    contrato_instance = Contrato.objects.filter(alumno=alumno_instance).first()
    apoderado_instance = alumno_instance.apoderado

    if request.method == 'POST':
        # Si el formulario ha sido enviado
        if contrato:
            form = ContratoForm(request.POST, instance=contrato, alumno_instance=alumno_instance, apoderado_instance=apoderado_instance, establecimiento_instance=establecimiento)
        else:  # Si no existe un contrato, creamos uno nuevo
            form = ContratoForm(request.POST, alumno_instance=alumno_instance, apoderado_instance=apoderado_instance, establecimiento_instance=establecimiento)
            form.instance.alumno = alumno  # Asociar el contrato nuevo con el alumno
        
        if form.is_valid():
            contrato = form.save(commit=False)  # No guardar aún el contrato
            # Recuperar el apoderado por su ID del campo oculto
            apoderado_id = form.cleaned_data['apoderado_id']
            apoderado = Apoderado.objects.get(id=apoderado_id)
            contrato.apoderado = apoderado
            contrato.alumno = alumno_instance
            contrato.save()  # Guardar los cambios en el contrato

            messages.success(request, 'Los cambios han sido guardados con éxito.')
            # Redirigir de nuevo a la misma página después de guardar
            return redirect('editar_informe_asis', establecimiento_id=establecimiento.id, id=alumno.id)

    else:
        form = ContratoForm(instance=contrato_instance, alumno_instance=alumno_instance, apoderado_instance=apoderado_instance, establecimiento_instance=establecimiento)

    return render(request, 'asis_edicion_info_pago.html', {
        'form': form,
        'establecimiento': establecimiento,
        'alumno': alumno,
    })



#==================================================  Generar contrato PDF =================================================================
@login_required
def generar_pdf_contrato(request, id):
    alumno = get_object_or_404(Alumno, id=id)
    contrato = Contrato.objects.filter(alumno=alumno).first()

    if contrato is None:
        return HttpResponse("No se encontró el contrato asociado al alumno.", status=404)

    # Obtener el nombre del establecimiento de forma segura
    establecimiento_nombre = alumno.establecimiento.nombre if alumno.establecimiento else "Establecimiento no disponible"

    # Cargar la plantilla HTML
    context = {
        'alumno': alumno,
        'contrato': contrato,
        'establecimiento_nombre': establecimiento_nombre,  # Pasar solo el nombre del establecimiento
    }

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

 # =================================================== Subdirector - editar Curso ===============================================
@login_required
def editar_recurso(request, curso_id):
    # Obtener el subdirector relacionado con el usuario autenticado
    subdirector = Subdirector.objects.get(user=request.user)
    
    # Obtener el curso a editar
    curso = get_object_or_404(Curso, id=curso_id)

    # Si el formulario ha sido enviado y es válido, actualizamos el curso
    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso, subdirector=subdirector)
        if form.is_valid():
            # Asignar el establecimiento_id del subdirector al curso antes de guardar
            curso.establecimiento = subdirector.establecimiento
            form.save()  # Guardamos los cambios
            return redirect('gestion_recursos_academicos')  # Redirige a la lista de recursos académicos
    else:
        form = CursoForm(instance=curso, subdirector=subdirector)

    return render(request, 'subdire_recursos.html', {'form': form})


# =================================================== Subdirector - Detalle de Curso ===================================================
@login_required
def detalle_curso(request, curso_id):
    # Obtener el subdirector relacionado con el usuario autenticado
    subdirector = Subdirector.objects.get(user=request.user)
    
    # Obtener el curso solo si pertenece al establecimiento del subdirector
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=subdirector.establecimiento)
    
    # Filtrar los estudiantes relacionados con el curso y establecimiento del subdirector
    estudiantes = Alumno.objects.filter(
        curso_alumno_relacion__curso=curso,
        establecimiento=subdirector.establecimiento
    ).distinct()

    # Calcular las calificaciones y el promedio de cada estudiante
    estudiantes_con_calificaciones_y_promedio = []
    for estudiante in estudiantes:
        # Obtener todas las calificaciones de un estudiante en ese curso
        calificaciones = Calificacion.objects.filter(alumno=estudiante, curso=curso)
        
        # Obtener el promedio de las calificaciones
        promedio = calificaciones.aggregate(promedio=Avg('nota'))['promedio']
        
        # Crear una lista de calificaciones
        lista_calificaciones = [calificacion.nota for calificacion in calificaciones]
        
        estudiantes_con_calificaciones_y_promedio.append({
            'id': estudiante.id,
            'nombre': estudiante.nombre,
            'apellido': estudiante.apellido,
            'calificaciones': lista_calificaciones,
            'promedio_notas': round(promedio, 2) if promedio is not None else "-"  # Verifica si el promedio es None
        })

    return render(request, 'detalle_curso.html', {'curso': curso, 'estudiantes': estudiantes_con_calificaciones_y_promedio})



# =================================================== Subdirector - Detalle de Curso en PDF ===================================================
@login_required
def detalle_curso_pdf(request, curso_id):
    # Obtener el subdirector relacionado con el usuario autenticado
    subdirector = Subdirector.objects.get(user=request.user)
    
    # Obtener el curso solo si pertenece al establecimiento del subdirector
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=subdirector.establecimiento)
    
    # Filtrar los estudiantes que pertenecen al establecimiento del subdirector y están en el curso
    estudiantes = Alumno.objects.filter(curso_alumno_relacion__curso=curso, establecimiento=subdirector.establecimiento).distinct()

    # Calcular el promedio de notas de cada estudiante y obtener las calificaciones
    estudiantes_con_notas = []
    for estudiante in estudiantes:
        # Obtener todas las calificaciones del estudiante para este curso
        calificaciones = Calificacion.objects.filter(alumno=estudiante, curso=curso)
        
        # Obtener las notas en una lista y calcular el promedio
        notas = [calificacion.nota for calificacion in calificaciones]
        promedio = sum(notas) / len(notas) if len(notas) > 0 else None
        
        # Manejar el caso cuando no haya calificaciones
        promedio_notas = round(promedio, 2) if promedio is not None else "-"
        
        estudiantes_con_notas.append({
            'nombre': estudiante.nombre,
            'apellido': estudiante.apellido,
            'notas': ' - '.join(map(str, notas)),  # Unir las notas con un guion
            'promedio_notas': promedio_notas
        })
    
    # Renderizar el HTML para el PDF
    html_string = render_to_string('detalle_curso_pdf.html', {'curso': curso, 'estudiantes': estudiantes_con_notas})
    
    # Generar el PDF con WeasyPrint
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


