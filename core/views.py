from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Curso, Asistencia

#Páginas
def home(request):
    return render(request, 'core/home.html')

def login_view(request):
    return render(request, 'login.html')

#DIRECTOR

def director_view(request):
    return render(request, 'director.html')

def directorFinanzas_view(request):
    return render(request, 'directorFinanzas.html')

def directorInforme_view(request):
    return render(request, 'directorInforme.html') 

def directorMenu_view(request):
    return render(request, 'directorMenu.html')

def directorPlanificacion_view(request):
    return render(request, 'directorPlanificacion.html')

#ESTUDIANTE


def estudiante_view(request):
    return render(request, 'estudiante.html')

def sostenedor_view(request):
    return render(request, 'sostenedor.html')

def estudiante_pru_base(request):
    return render(request, 'estudiante_pru_base.html')

#APODERADO

def apoderado_view(request):
    return render(request, 'apoderado.html')

def apoderadoAsistencia_view(request):
    return render(request, 'apoderadoAsistencia.html')

def apoderadoMatricula_view(request):
    return render(request, 'apoderadoMatricula.html')

#PROFESOR
class AsistenciaCursoView(View):
    def get(self, request, curso_id):
        curso = get_object_or_404(Curso, id=curso_id)
        asistencia = Asistencia.objects.filter(curso=curso).order_by('estudiante__nombre')
        return render(request, 'asistencia/curso.html', {'curso': curso, 'asistencia': asistencia})