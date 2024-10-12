# urls.py
from django.urls import path
from .views import login_view,profesor_dashboard,profesor_cursos,crear_usuario_db

urlpatterns = [
    path('login/', login_view, name='login'),
  #  path('dashboard/', dashboard_view, name='dashboard'),  # Aquí iría la vista del dashboard
    path('profesor/', profesor_dashboard, name='profesor'),
    path('profesor/cursos/', profesor_cursos, name='profesor_cursos'),  # Ruta para "Mis cursos"
    path('crear_db_usuarios', crear_usuario_db, name='crear_usuarios'),
]

