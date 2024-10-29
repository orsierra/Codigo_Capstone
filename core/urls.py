# urls.py
from django.urls import path
from .views import login_view, profesor_dashboard, profesor_cursos, crear_usuario_db, registrar_calificaciones, registro_academico, observaciones,libro_clases, apoderadoConsuAsis, apoderadoConsuNotas, apoderado_view, director_dashboard, update_curso, descargar_pdf_alumno, direcPdfInfoAca, direcPdfPlanificacion
from core import views


urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', login_view, name='login'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
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
    path('alumno_detalle/<int:alumno_id>/', views.alumno_detalle, name='alumno_detalle'),
    path('alumno_detalle/<int:alumno_id>/descargar_pdf/', descargar_pdf_alumno, name='descargar_pdf_alumno'),  # descarga detalles del alumno en pdf
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
    path('observaciones/', views.apoderado_observaciones, name='apoderadoObservaciones'),
    #Director
    path('director/', director_dashboard, name='director_dashboard'),
    path('director/consulta-informes/', views.directorMenu, name='director_menu'),
    path('planificacion-academica/', views.director_plani, name='director_plani'),
    path('informes-academicos/', views.informes_academicos, name='informes_academicos'),
    path('update-curso/', update_curso, name='update_curso'),
    path('informe-academico/pdf/', direcPdfInfoAca, name='direcPdfInfoAca'),
    path('planificacion-academica/pdf/', views.direcPdfPlanificacion, name='direcPdfPlanificacion'),
    path('informe-financiero/', views.informe_financiero_view, name='informe_financiero'),
    path('informe-financiero/eliminar/<int:informe_id>/', views.eliminar_informe_view, name='eliminar_informe'),
    path('informe-financiero/pdf/', views.generar_pdf_view, name='descargar_pdf'),
    # Asistende De admision y Matricula
    path('gestionar_estudiantes/', views.gestionar_estudiantes, name='gestionar_estudiantes'),
    path('agregar_alumno/', views.agregar_alumno, name='agregar_alumno'),
    path('actualizar_matricula/<int:id>/', views.actualizar_matricula, name='actualizar_matricula'),
    path('panel_admision/', views.panel_admision, name='panel_admision'),
    path('eliminar_alumno/<int:alumno_id>/', views.eliminar_alumno, name='eliminar_alumno'),
    # Asistente de admision y finanza
    path('panel_asisAdminFinan/', views.asisAdminFinan_dashboard, name='panel_asisAdminFinan'),
    path('gestion-pagos-admision/', views.ver_gestion_pagos_admision, name='asisAdmiFinan_gestion_pagos'),
    path('eliminar-alumno-asis/<int:id>/', views.eliminar_alumno_asis, name='eliminar_alumno_asis'),
    path('agregar-alumno-asis/', views.agregar_alumno_asis, name='agregar_alumno_asis'),
    path('editar-informe-asis/<int:id>/', views.editar_informe_asis, name='editar_informe_asis'),
    path('generar_pdf_contrato/<int:id>/', views.generar_pdf_contrato, name='generar_pdf_contrato'),



]