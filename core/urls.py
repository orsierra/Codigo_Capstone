# urls.py
from django.urls import path
from .views import login_view, profesor_dashboard, profesor_cursos, crear_usuario_db, registrar_calificaciones, registro_academico, observaciones,libro_clases, apoderadoConsuAsis, apoderadoConsuNotas, apoderadoMatri, apoderado_view, director_dashboard, update_curso
from core import views


urlpatterns = [
    path('login/', login_view, name='login'),
  #  path('dashboard/', dashboard_view, name='dashboard'),  # Aquí iría la vista del dashboard
    path('profesor/', profesor_dashboard, name='profesor'),
    path('profesor/cursos/', profesor_cursos, name='profesor_cursos'),  # Ruta para "Mis cursos"
    path('crear_db_usuarios', crear_usuario_db, name='crear_usuarios'),
    #Profesor mis cursos
    path('libro-clases/<int:curso_id>/', libro_clases, name='profesor_libro'),
    path('registrar-asistencia/<int:curso_id>/', views.registrar_asistencia, name='registrar_asistencia'),
    path('registrar-calificaciones/<int:curso_id>/', registrar_calificaciones, name='registrar_calificaciones'),  
    path('registro-academico/<int:curso_id>/', registro_academico, name='registro_academico'),
    path('generar-informes/<int:curso_id>/', views.generar_informes, name='generar_informes'),
    path('observaciones/<int:curso_id>/', observaciones, name='observaciones'),
    #alumno
    path('alumno/', views.alumno_dashboard, name='alumno_dashboard'),
    path('alumno/asistencia/', views.alumno_consulta_asistencia, name='alumnoConsuAsis'),
    path('alumno/notas/', views.alumno_consulta_notas, name='alumnoConsuNotas'),
    path('alumno/', views.alumno_home, name='alumno_home'),
    #Apoderado
    path('apoderado/', apoderado_view, name='apoderado_view'),  # Dashboard del apoderado
    path('consulta-asistencia/', apoderadoConsuAsis, name='apoderadoConsuAsis'),  # Consulta de asistencia
    path('apoderado/consulta-notas/', apoderadoConsuNotas, name='apoderadoConsuNotas'),  # Consulta de notas
    path('apoderado/matricula/', apoderadoMatri, name='apoderadoMatri'),
    #Director
    path('director/', director_dashboard, name='director_dashboard'),
    path('director/consulta-informes/', views.directorMenu, name='director_menu'),
    path('planificacion-academica/', views.director_plani, name='director_plani'),
    path('informes-academicos/', views.informes_academicos, name='informes_academicos'),
    path('informes-finanzas/', views.informes_finanzas, name='informes_finanzas'),
    path('update-curso/', update_curso, name='update_curso'),
    # Asistende De admision y Matricula
    path('gestionar_estudiantes/', views.gestionar_estudiantes, name='gestionar_estudiantes'),
    path('agregar_alumno/', views.agregar_alumno, name='agregar_alumno'),
    path('actualizar_matricula/<int:id>/', views.actualizar_matricula, name='actualizar_matricula'),
    path('panel_admision/', views.panel_admision, name='panel_admision'),
    path('eliminar_alumno/<int:alumno_id>/', views.eliminar_alumno, name='eliminar_alumno'),

]