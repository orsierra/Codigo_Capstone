
from django.shortcuts import render

#Páginas
def home(request):
    return render(request, 'core/home.html')

def login_view(request):
    return render(request, 'login.html')

def director_view(request):
    return render(request, 'director.html')

def estudiante_view(request):
    return render(request, 'estudiante.html')

def sostenedor_view(request):
    return render(request, 'sostenedor.html')

def estudiante_pru_base(request):
    return render(request, 'estudiante_pru_base.html')

