# urls.py
from django.urls import path
from .views import login_view, profesor_dashboard, profesor_cursos, crear_usuario_db, registrar_calificaciones, registro_academico, observaciones,libro_clases, apoderadoConsuAsis, apoderadoConsuNotas, apoderado_view, director_dashboard, update_curso, descargar_pdf_alumno, direcPdfInfoAca,sostenedor,establecimientos
from core import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
  #  path('dashboard/', dashboard_view, name='dashboard'),  # Aquí iría la vista del dashboard
    path('profesor/<int:establecimiento_id>/', profesor_dashboard, name='profesor'),
    # en urls.py
    path('profesor/<int:establecimiento_id>/cursos/', profesor_cursos, name='profesor_cursos'),
  # Ruta para "Mis cursos"
    path('crear_db_usuarios', crear_usuario_db, name='crear_usuarios'),
    #Profesor mis cursos
    # En urls.py
    path('libro-clases/<int:establecimiento_id>/<int:curso_id>/', libro_clases, name='libro_clases'),
    path('registrar-asistencia/<int:establecimiento_id>/<int:curso_id>/', views.registrar_asistencia, name='registrar_asistencia'),
    path('registrar-calificaciones/<int:establecimiento_id>/<int:curso_id>/', registrar_calificaciones, name='registrar_calificaciones'),  
    path('registro-academico/<int:establecimiento_id>/<int:curso_id>/', registro_academico, name='registro_academico'),
    path('generar-informes/<int:establecimiento_id>/<int:curso_id>/', views.generar_informes, name='generar_informes'),
    path('alumno_detalle/<int:establecimiento_id>/<int:alumno_id>/', views.alumno_detalle, name='alumno_detalle'),
    path('alumno_detalle/<int:establecimiento_id>/<int:alumno_id>/descargar_pdf/', descargar_pdf_alumno, name='descargar_pdf_alumno'),  # descarga detalles del alumno en pdf
    path('observaciones/<int:establecimiento_id>/<int:alumno_id>/', views.observaciones, name='observaciones'),



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
    # Asistente De admision y Matricula
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
    
    #SUBDIRECTOR
    path('subdirector/', views.subdirector_home, name='subdirector_home'),
    path('subdirector/informes/', views.consulta_informes_academicos, name='consulta_informes_academicos'),
    path('subdirector/recursos/', views.gestion_recursos_academicos, name='gestion_recursos_academicos'),
    path('subdirector/curso/<int:curso_id>/', views.detalle_curso, name='detalle_curso'),
    path('curso/<int:curso_id>/pdf/', views.detalle_curso_pdf, name='detalle_curso_pdf'),
    
    #SOSTENEDOR
    path('sostenedor/', views.sostenedor, name='sostenedor'),
    path('establecimientos/<int:establecimiento_id>/', views.establecimientos, name='establecimientos'),




]