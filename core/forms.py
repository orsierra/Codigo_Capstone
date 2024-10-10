
from django import forms
from .models import Evaluacion, Asistencia

class EvaluacionForm(forms.ModelForm):
    class Meta:
        model = Evaluacion
        fields = ['estudiante', 'tipo_evaluacion', 'nota', 'asignatura']
        widgets = {
            'tipo_evaluacion': forms.TextInput(attrs={'class': 'form-control'}),
            'nota': forms.NumberInput(attrs={'class': 'form-control'}),
            'estudiante': forms.Select(attrs={'class': 'form-control'}),
            'asignatura': forms.Select(attrs={'class': 'form-control'}),
        }

class AsistenciaForm(forms.ModelForm):
    class Meta:
        model = Asistencia
        fields = ['estudiante', 'curso', 'presente', 'justificado']
        widgets = {
            'presente': forms.RadioSelect(),
            'justificado': forms.RadioSelect(),
        }