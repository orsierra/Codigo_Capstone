from django import forms
from .models import Asistencia, Calificacion

class AsistenciaForm(forms.ModelForm):
    class Meta:
        model = Asistencia
        fields = ['alumno', 'curso', 'fecha', 'presente']

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['alumno', 'curso', 'calificacion']