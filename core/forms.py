from django import forms
from .models import Asistencia, Alumno, Calificacion

class AsistenciaForm(forms.ModelForm):
    class Meta:
        model = Asistencia
        fields = ['curso', 'fecha']  # Puedes quitar el campo 'alumno' porque será manejado en la vista y el HTML.

    # Agregar campos dinámicamente para los alumnos
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'alumnos' in kwargs:
            for alumno in kwargs['alumnos']:
                self.fields[f'presente_{alumno.id}'] = forms.BooleanField(required=False, label=f'{alumno.nombre} {alumno.apellido} presente')
                self.fields[f'ausente_{alumno.id}'] = forms.BooleanField(required=False, label=f'{alumno.nombre} {alumno.apellido} ausente')
                self.fields[f'justificado_{alumno.id}'] = forms.BooleanField(required=False, label=f'{alumno.nombre} {alumno.apellido} justificado')


class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['nota']  # Solo vamos a editar la nota

    # Personalización para que el formulario se muestre más bonito
    def __init__(self, *args, **kwargs):
        super(CalificacionForm, self).__init__(*args, **kwargs)
        self.fields['nota'].widget.attrs.update({'class': 'form-control'})