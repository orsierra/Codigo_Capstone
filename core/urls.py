from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='login'),
    path('login/', views.login_view, name='login'),
    #DIRECTOR
    path('director/', views.director_view, name='director'),
    path('directorFinanzas/',views.directorFinanzas_view, name='directorFinanzas'),
    path('directorInforme/',views.directorInforme_view, name='directorInforme'),
    path('directorMenu/',views.directorMenu_view, name='directorMenu'),
    path('directorPlanificacion/',views.directorPlanificacion_view, name='directorPlanificacion'),    
    #PROFESOR
    path('profesorAsistencia/', views.profesorAsistencia_view, name='profesorAsistencia'),
    path('profesorCalificacion/', views.profesorCalificacion_view, name='profesorCalificacion'),
    path('profesorMisCursos/', views.profesorMisCursos_view, name='profesorMisCursos'),
    path('profesorObservacion/', views.profesorObservacion_view, name='profesorObservacion'),
      
      
    path('estudiante/', views.estudiante_view, name='estudiante'),
    path('sostenedor/', views.sostenedor_view, name='sostenedor'),
    path('estudiante_pru_base/', views.estudiante_pru_base, name='estudiante_pru_base'), 
    
    #APODERADO
    path('apoderado/',views.apoderado_view, name ='apoderado'),
    path('apoderadoAsistencia/', views.apoderadoAsistencia_view, name='apoderadoAsistencia'),
    path('apoderadoMatricula/', views.apoderadoMatricula_view, name='apoderadoMatricula'),
]