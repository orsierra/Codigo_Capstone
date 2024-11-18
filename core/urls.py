# urls.py
from django.urls import path
from .views import login_view, profesor_dashboard, profesor_cursos, registrar_calificaciones, registro_academico, observaciones,libro_clases, apoderadoConsuAsis, apoderadoConsuNotas, apoderado_view, director_dashboard, update_curso, descargar_pdf_alumno, direcPdfInfoAca,sostenedor,establecimientos
from core import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('quienes-somos/', views.quienes_somos, name='quienes_somos'),
    #path('dashboard/', dashboard_view, name='dashboard'),  # Aquí iría la vista del dashboard
    path('profesor/<int:establecimiento_id>/', profesor_dashboard, name='profesor'),
    path('profesor/<int:establecimiento_id>/cursos/', profesor_cursos, name='profesor_cursos'),
    #Profesor mis cursos
    path('libro-clases/<int:establecimiento_id>/<int:curso_id>/', libro_clases, name='libro_clases'),
    path('registrar-asistencia/<int:establecimiento_id>/<int:curso_id>/', views.registrar_asistencia, name='registrar_asistencia'),
    path('registrar-calificaciones/<int:establecimiento_id>/<int:curso_id>/', registrar_calificaciones, name='registrar_calificaciones'),  
    path('registro-academico/<int:establecimiento_id>/<int:curso_id>/', registro_academico, name='registro_academico'),
    path('generar-informes/<int:establecimiento_id>/<int:curso_id>/', views.generar_informes, name='generar_informes'),
    path('alumno_detalle/<int:establecimiento_id>/<int:alumno_id>/', views.alumno_detalle, name='alumno_detalle'),
    path('alumno_detalle/<int:establecimiento_id>/<int:alumno_id>/descargar_pdf/', descargar_pdf_alumno, name='descargar_pdf_alumno'),
    path('observaciones/<int:establecimiento_id>/<int:curso_id>/', views.observaciones, name='observaciones'),
    path('historial_bitacoras/<int:establecimiento_id>/<int:curso_id>/', views.historial_bitacoras, name='historial_bitacoras'),
    path('eliminar_bitacora/<int:establecimiento_id>/<int:bitacora_id>/', views.eliminar_bitacora, name='eliminar_bitacora'),
    #alumno
    path('alumno/<int:establecimiento_id>/', views.alumno_dashboard, name='alumno_dashboard'),
    path('alumno/asistencia/<int:establecimiento_id>/', views.alumno_consulta_asistencia, name='alumnoConsuAsis'),
    path('alumno/notas/<int:establecimiento_id>/', views.alumno_consulta_notas, name='alumnoConsuNotas'),
    #Apoderado
    path('apoderado/<int:establecimiento_id>/consulta_asistencia/', views.apoderadoConsuAsis, name='apoderadoConsuAsis'),
    path('apoderado/<int:establecimiento_id>/consulta_notas/', views.apoderadoConsuNotas, name='apoderadoConsuNotas'),
    path('apoderado/<int:establecimiento_id>/observaciones/', views.apoderado_observaciones, name='apoderadoObservaciones'),
    path('apoderado/<int:establecimiento_id>/', views.apoderado_view, name='apoderado_view'),
    path('historial-notificaciones/<int:establecimiento_id>/', views.historial_notificaciones, name='historial_notificaciones'),
    path('apoderado/<int:establecimiento_id>/notificacion/<int:notificacion_id>/leer/', views.marcar_notificacion_como_leida, name='marcar_notificacion_como_leida'),
    path('apoderado/<int:establecimiento_id>/marcar-notificacion/<int:notificacion_id>/', views.marcar_notificacion_como_leida, name='marcar_notificacion_como_leida_alt'),
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
    path('panel_admision/<int:establecimiento_id>/', views.panel_admision, name='panel_admision'),
    path('eliminar_alumno/<int:alumno_id>/', views.eliminar_alumno, name='eliminar_alumno'),
    # Asistente de admision y finanza
    path('panel_asisAdminFinan/<int:establecimiento_id>/', views.asisAdminFinan_dashboard, name='panel_asisAdminFinan'),
    path('gestion-pagos-admision/<int:establecimiento_id>/', views.ver_gestion_pagos_admision, name='asisAdmiFinan_gestion_pagos'),
    path('editar-informe-asis/<int:establecimiento_id>/<int:id>/', views.editar_informe_asis, name='editar_informe_asis'),
    path('generar_pdf_contrato/<int:id>/', views.generar_pdf_contrato, name='generar_pdf_contrato'),
    path('agregar-alumno/<int:establecimiento_id>/', views.agregar_alumno_asis, name='agregar_alumno_asis'),
    path('eliminar-alumno/<int:establecimiento_id>/<int:alumno_id>/', views.eliminar_alumno_asis, name='eliminar_alumno_asis'),
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