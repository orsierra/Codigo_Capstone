# urls.py
from django.urls import path
from .views import login_view,profesor_dashboard,profesor_cursos,crear_usuario_db,registrar_asistencia, registrar_calificaciones, registro_academico, generar_informes, observaciones,libro_clases,alumno_consulta_asistencia,alumno_dashboard,alumno_consulta_notas,alumno_home
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
    path('registrar-calificaciones/<int:curso_id>/', registrar_calificaciones, name='registrar_calificaciones'),  # Asegúrate de usar curso_id
    #path('registrar_calificacion/', registrar_calificaciones, name='registrar_calificacion'),
    path('registro-academico/', views.registro_academico, name='registro_academico'),
    path('generar-informes/', views.generar_informes, name='generar_informes'),
    path('observaciones/', views.observaciones, name='observaciones'),
    #alumno
    path('alumno/', views.alumno_dashboard, name='alumno_dashboard'),
    path('alumno/asistencia/', views.alumno_consulta_asistencia, name='alumnoConsuAsis'),
    path('alumno/notas/', views.alumno_consulta_notas, name='alumnoConsuNotas'),
    path('alumno/', views.alumno_home, name='alumno_home'),
    
    
    # URL DE LIBRO

]