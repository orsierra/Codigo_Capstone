<<<<<<< HEAD
from django import forms
from .models import Evaluacion, Estudiante, Asignatura

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
=======
# core/forms.py
from django import forms
from .models import Apoderado
>>>>>>> e1f7bcd9eaa9abdcbc74941e153ff435464758bd
