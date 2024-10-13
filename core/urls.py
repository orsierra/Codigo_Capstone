# urls.py
from django.urls import path
from .views import login_view,profesor_dashboard,profesor_cursos,crear_usuario_db
from .views import registrar_asistencia, registrar_calificaciones, registro_academico, generar_informes, observaciones, profesor_libro


urlpatterns = [
    path('login/', login_view, name='login'),
  #  path('dashboard/', dashboard_view, name='dashboard'),  # Aquí iría la vista del dashboard
    path('profesor/', profesor_dashboard, name='profesor'),
    path('profesor/cursos/', profesor_cursos, name='profesor_cursos'),  # Ruta para "Mis cursos"
    path('crear_db_usuarios', crear_usuario_db, name='crear_usuarios'),
    #Profesor mis cursos
    path('curso/<int:curso_id>/asistencia/', registrar_asistencia, name='registrar_asistencia'),
    path('curso/<int:curso_id>/calificaciones/', registrar_calificaciones, name='registrar_calificaciones'),
    path('curso/<int:curso_id>/registro_academico/', registro_academico, name='registro_academico'),
    path('curso/<int:curso_id>/informes/', generar_informes, name='generar_informes'),
    path('curso/<int:curso_id>/observaciones/', observaciones, name='observaciones'),
    # URL DE LIBRO
    path('profesor/libro/<int:curso_id>/', profesor_libro, name='profesor_libro'),
]

