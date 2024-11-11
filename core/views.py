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
    profesor = curso.profesor

    # Obtener los alumnos aprobados para el curso específico y establecimiento
    alumnos_aprobados = CursoAlumno.objects.filter(
        curso=curso, 
        alumno__estado_admision='Aprobado', 
        curso__establecimiento=establecimiento
    ).select_related('alumno')

    if not alumnos_aprobados.exists():
        messages.warning(request, f"No hay alumnos aprobados asociados al curso {curso.nombre}.")
        return redirect('profesor_cursos', establecimiento_id=establecimiento_id)

    success_message = None

    if request.method == 'POST':
        actividades_realizadas = request.POST.get('actividades_realizadas')
        observaciones = request.POST.get('observaciones')

        if not actividades_realizadas:
            success_message = "Debe registrar las actividades realizadas en la bitácora antes de guardar la asistencia."
        else:
            # Guardar en la bitácora de clase
            BitacoraClase.objects.create(
                curso=curso,
                fecha=timezone.now(),
                profesor=profesor,
                actividades_realizadas=actividades_realizadas,
                observaciones=observaciones,
            )

            # Crear y guardar el objeto de Asistencia
            asistencia = Asistencia(curso=curso, fecha=timezone.now(), establecimiento=establecimiento)
            asistencia.save()

            # Registrar el estado de asistencia para cada alumno aprobado
            for curso_alumno in alumnos_aprobados:
                alumno = curso_alumno.alumno
                asistencia_estado = request.POST.get(f'asistencia_{alumno.id}')

                if asistencia_estado == 'presente':
                    asistencia.alumnos_presentes.add(alumno)
                elif asistencia_estado == 'ausente':
                    asistencia.alumnos_ausentes.add(alumno)
                elif asistencia_estado == 'justificado':
                    asistencia.alumnos_justificados.add(alumno)

            success_message = "Bitácora y asistencia registradas exitosamente."
            messages.success(request, success_message)
            return redirect('registrar_asistencia', establecimiento_id=establecimiento_id, curso_id=curso.id)

    return render(request, 'registrarAsistencia.html', {
        'curso': curso,
        'alumnos_aprobados': alumnos_aprobados,
        'success_message': success_message,
        'establecimiento': establecimiento,
    })



@login_required
def historial_bitacoras(request, establecimiento_id, curso_id):
    # Obtener el establecimiento
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    
    # Obtener el curso asociado al establecimiento
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=establecimiento)  # Aseguramos que el curso pertenece al establecimiento
    
    # Obtener las bitácoras asociadas al curso
    bitacoras = BitacoraClase.objects.filter(curso=curso).order_by('-fecha')  # Ordenadas por fecha descendente
    
    # Preparar el contexto para la plantilla
    context = {
        'curso': curso,
        'establecimiento': establecimiento,  # Agregar establecimiento al contexto
        'bitacoras': bitacoras,
    }
    return render(request, 'historial_bitacoras.html', context)




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

    # Obtener alumnos aprobados para el curso y establecimiento específicos
    alumnos_aprobados = CursoAlumno.objects.filter(
        curso=curso, 
        alumno__estado_admision='Aprobado', 
        curso__establecimiento=establecimiento
    ).select_related('alumno')

    if request.method == 'POST':
        for curso_alumno in alumnos_aprobados:
            alumno = curso_alumno.alumno
            form = CalificacionForm(request.POST, prefix=str(alumno.id))
            if form.is_valid():
                # Obtener o crear la calificación del alumno
                calificacion, created = Calificacion.objects.get_or_create(
                    alumno=alumno,
                    curso=curso,
                    establecimiento=establecimiento,
                    defaults={'nota': form.cleaned_data['nota']}
                )
                if not created:
                    # Si ya existe la calificación, actualizar la nota
                    calificacion.nota = form.cleaned_data['nota']
                    calificacion.save()
            else:
                errores[alumno] = form.errors

        if not errores:
            messages.success(request, "Se han guardado los cambios exitosamente.")
            return redirect('registrar_calificaciones', establecimiento_id=establecimiento_id, curso_id=curso_id)

    else:
        # Crear un formulario vacío para cada alumno aprobado
        form_list = {curso_alumno.alumno: CalificacionForm(prefix=str(curso_alumno.alumno.id)) for curso_alumno in alumnos_aprobados}

    return render(request, 'registrarCalificaciones.html', {
        'curso': curso,
        'form_list': form_list,
        'errores': errores,
        'establecimiento': establecimiento,
    })
# =================================================== REGISTRO ACADEMICO =====================================================================================

@login_required
def registro_academico(request, establecimiento_id, curso_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=establecimiento)

    # Filtrar solo alumnos aprobados en el curso y establecimiento especificados
    curso_alumnos = CursoAlumno.objects.filter(curso=curso, alumno__estado_admision='Aprobado')
    alumnos_aprobados = [curso_alumno.alumno for curso_alumno in curso_alumnos]

    # Obtener calificaciones y asistencias para el curso
    calificaciones = Calificacion.objects.filter(curso=curso, establecimiento=establecimiento)
    asistencias = Asistencia.objects.filter(curso=curso)

    # Construir diccionarios para mapear alumnos con sus calificaciones, promedios y asistencias
    calificaciones_por_alumno = {}
    promedios_por_alumno = {}
    asistencias_por_alumno = {}

    for alumno in alumnos_aprobados:
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
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    curso = get_object_or_404(Curso, id=curso_id, establecimiento=establecimiento)

    # Filtra los CursoAlumno que correspondan al curso y establecimiento, y por estado de admisión 'Aprobado'
    curso_alumnos = CursoAlumno.objects.filter(curso=curso)
    print("Curso Alumnos:", curso_alumnos)  # Agrega esto para verificar los alumnos del curso
    
    alumnos_aprobados = Alumno.objects.filter(
        curso_alumno_relacion__in=curso_alumnos,
        estado_admision='Aprobado',
        establecimiento=establecimiento
    )
    print("Alumnos Aprobados:", alumnos_aprobados)  # Agrega esto para verificar los alumnos aprobados

    return render(request, 'Profe_generar_informes.html', {
        'curso': curso,
        'alumnos_aprobados': alumnos_aprobados,
        'establecimiento': establecimiento
    })



# Alumno detalle para generar informe en PDF
@login_required
def alumno_detalle(request, establecimiento_id, alumno_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    alumno = get_object_or_404(Alumno, id=alumno_id, establecimiento=establecimiento)

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
            'observaciones': [],  # Agregar observaciones vacías en el contexto
            'promedio': 0,
            'establecimiento': establecimiento,  # Agregar establecimiento al contexto
        })

    # Filtrar calificaciones del alumno por el curso actual
    calificaciones = Calificacion.objects.filter(alumno=alumno, curso=curso_actual)

    # Calcular el promedio de calificaciones
    promedio = calificaciones.aggregate(promedio=Avg('nota'))['promedio'] or 0

    # Filtrar asistencias, ausencias y justificaciones usando el curso actual
    asistencias = Asistencia.objects.filter(curso=curso_actual, alumnos_presentes=alumno)
    ausencias = Asistencia.objects.filter(curso=curso_actual, alumnos_ausentes=alumno)
    justificaciones = Asistencia.objects.filter(curso=curso_actual, alumnos_justificados=alumno)

    # Filtrar observaciones del alumno por el curso actual
    observaciones = Observacion.objects.filter(alumno=alumno, curso=curso_actual)

    context = {
        'alumno': alumno,
        'curso': curso_actual,
        'calificaciones': calificaciones,
        'asistencias': asistencias,
        'ausencias': ausencias,
        'justificaciones': justificaciones,
        'observaciones': observaciones,  # Incluir observaciones en el contexto
        'promedio': promedio,
        'establecimiento': establecimiento  # Incluir establecimiento en el contexto
    }
    return render(request, 'alumno_detalle.html', context)

##============================================ generar pdf por alumno: asistencia y calificaciones================================

@login_required
def descargar_pdf_alumno(request, establecimiento_id, alumno_id):
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)
    alumno = get_object_or_404(Alumno, id=alumno_id, establecimiento=establecimiento)
    
    # Obtener las calificaciones, asistencias, y observaciones del alumno
    calificaciones = Calificacion.objects.filter(alumno=alumno)
    asistencias = Asistencia.objects.filter(alumnos_presentes=alumno)
    ausencias = Asistencia.objects.filter(alumnos_ausentes=alumno)
    justificaciones = Asistencia.objects.filter(alumnos_justificados=alumno)
    observaciones = Observacion.objects.filter(alumno=alumno)  # Obtener las observaciones del alumno

    # Calcular el promedio de calificaciones
    promedio = calificaciones.aggregate(promedio=Avg('nota'))['promedio'] or 0

    # Preparar el contexto para la plantilla
    context = {
        'alumno': alumno,
        'calificaciones': calificaciones,
        'asistencias': asistencias,
        'ausencias': ausencias,
        'justificaciones': justificaciones,
        'observaciones': observaciones,  # Añadir las observaciones al contexto
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
def observaciones(request, establecimiento_id, curso_id):
    # Obtener el establecimiento y el curso asociado al establecimiento
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)  # Obtener el establecimiento
    curso = get_object_or_404(Curso, id=curso_id)  # Obtener el curso
    observaciones = Observacion.objects.filter(curso=curso)

    # Filtra solo los alumnos aprobados a través de CursoAlumno
    alumnos_aprobados = Alumno.objects.filter(curso_alumno_relacion__curso=curso, estado_admision='Aprobado')

    if request.method == 'POST':
        if 'eliminar' in request.POST:
            observacion_id = request.POST.get('observacion_id')
            observacion = get_object_or_404(Observacion, id=observacion_id)
            observacion.delete()
            return redirect('observaciones', establecimiento_id=establecimiento.id, curso_id=curso.id)  # Redirigir después de eliminar

        # Lógica para agregar una nueva observación
        form = ObservacionForm(request.POST)
        form.fields['alumno'].queryset = alumnos_aprobados  # Filtrar alumnos aprobados
        if form.is_valid():
            observacion = form.save(commit=False)
            observacion.curso = curso  # Asociar la observación al curso
            observacion.save()
            return redirect('observaciones', establecimiento_id=establecimiento.id, curso_id=curso.id)  # Redirigir después de guardar
    else:
        form = ObservacionForm()
        form.fields['alumno'].queryset = alumnos_aprobados  # Filtrar alumnos aprobados

    return render(request, 'observaciones.html', {
        'establecimiento': establecimiento,  # Añadir el establecimiento al contexto
        'curso': curso,  # Añadir el curso al contexto
        'observaciones': observaciones,
        'form': form,
    })



# ============================================================= Dashboard de Alumno ==================================================

@login_required
def alumno_dashboard(request):
    return render(request, 'alumno.html')


# ===================================================== Consulta de Asistencia del Alumno ============================================

@login_required
def alumno_consulta_asistencia(request, establecimiento_id):
    # Obtener el objeto Alumno asociado al usuario actual
    alumno = get_object_or_404(Alumno, user=request.user)

    # Obtener el establecimiento por el ID pasado como parámetro
    establecimiento = get_object_or_404(Establecimiento, id=establecimiento_id)

    # Verificar el estado de admisión del alumno
    if alumno.estado_admision != 'Aprobado':
        messages.error(request, 'Su estado de admisión no le permite acceder a la consulta de asistencia.')
        return redirect('alumno_home')

    asistencias_data = []

    # Obtener los cursos en los que está inscrito el alumno a través de CursoAlumno
    cursos_alumno = CursoAlumno.objects.filter(alumno=alumno)

    for curso_alumno in cursos_alumno:
        curso = curso_alumno.curso  # Acceder al curso

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
    for curso_alumno in cursos_alumno:
        curso = curso_alumno.curso  # Acceder al curso
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


#============================================================================= Consulta de Asistencia del Apoderado =========================================================================================

@login_required
def apoderadoConsuAsis(request):
    apoderado = get_object_or_404(Apoderado, user=request.user)
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

            fechas_totales = fechas_presentes | fechas_ausentes | fechas_justificados
            total_clases = len(fechas_totales)

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

        # Obtener los cursos asignados al alumno a través de CursoAlumno
        cursos_asignados = CursoAlumno.objects.filter(alumno=alumno).select_related('curso')
        
        for curso_alumno in cursos_asignados:
            curso = curso_alumno.curso  # Obtener el curso desde CursoAlumno
            
            # Obtener las calificaciones del alumno para el curso específico
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

        # Verifica si el formulario es válido
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Verifica si el usuario ya existe
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
                except Exception as e:
                    form.add_error(None, f'Ocurrió un error inesperado: {str(e)}')
        else:
            # Mostrar errores del formulario en caso de que no sea válido
            print(form.errors)

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

    # Pasar el establecimiento_id en el contexto
    context = {
        'alumnos': alumnos,
        'establecimiento_id': establecimiento.id,  # solo pasamos el ID
    }

    return render(request, 'asisAdmiFinan_gestion_pagos.html', context)



# =====================================================VISTA de ASISTENTE DE ADMISIÓN Y FINANZAS PARA AGREGAR ALUMNO ==========================================
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
                return redirect('gestion_pagos_admision', establecimiento_id=establecimiento.id)
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







