from django.urls import path
from . import views
from .views import AsistenciaCursoView, planificacion_academica, imprimir_pdf

urlpatterns = [
    path('', views.home, name='login'),
    path('login/', views.login_view, name='login'),
    #DIRECTOR
    path('director/', views.director_view, name='director'),
    path('directorFinanzas/',views.directorFinanzas_view, name='directorFinanzas'),
    path('directorInforme/',views.directorInforme_view, name='directorInforme'),
    path('directorMenu/',views.directorMenu_view, name='directorMenu'),
    path('directorPlanificacion/',views.directorPlanificacion_view, name='directorPlanificacion'),  
    #Planificacion Academica
    path('planificacion/', planificacion_academica, name='planificacion_academica'),  
    path('planificacion/pdf/', imprimir_pdf, name='imprimir_pdf'),
    #PROFESOR
    
    path('asistencia/<int:curso_id>/', AsistenciaCursoView.as_view(), name='asistencia'),

    path('estudiante/', views.estudiante_view, name='estudiante'),
    path('sostenedor/', views.sostenedor_view, name='sostenedor'),
    path('estudiante_pru_base/', views.estudiante_pru_base, name='estudiante_pru_base'), 
    
    #APODERADO
    path('apoderado/',views.apoderado_view, name ='apoderado'),
    path('apoderadoAsistencia/', views.apoderadoAsistencia_view, name='apoderadoAsistencia'),
    path('apoderadoMatricula/', views.apoderadoMatricula_view, name='apoderadoMatricula'),
]