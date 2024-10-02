from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='login'),
    path('login/', views.login_view, name='login'),
    path('director/', views.director_view, name='director'),
    path('estudiante/', views.estudiante_view, name='estudiante'),
    path('sostenedor/', views.sostenedor_view, name='sostenedor'),
    path('estudiante_pru_base/', views.estudiante_pru_base, name='estudiante_pru_base'), 
]