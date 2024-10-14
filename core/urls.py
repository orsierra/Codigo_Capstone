# urls.py
from django.urls import path
from .views import login_view,profesor_dashboard,profesor_cursos,crear_usuario_db
from .views import registrar_asistencia, registrar_calificaciones, registro_academico, generar_informes, observaciones,libro_clases
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
    path('registrar-calificaciones/<int:curso_id>/', views.registrar_calificaciones, name='registrar_calificaciones'),
    path('registro-academico/', views.registro_academico, name='registro_academico'),
    path('generar-informes/', views.generar_informes, name='generar_informes'),
    path('observaciones/', views.observaciones, name='observaciones'),
    
    # URL DE LIBRO

]

