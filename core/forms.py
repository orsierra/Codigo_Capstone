from django import forms
from .models import Asistencia, Alumno, Calificacion, Observacion, Apoderado, Curso
from django.core.exceptions import ValidationError
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

    def __init__(self, *args, **kwargs):
        super(CalificacionForm, self).__init__(*args, **kwargs)
        self.fields['nota'].widget.attrs.update({'class': 'form-control'})


    def clean_nota(self):
        nota = self.cleaned_data.get('nota')
        if nota < 0 or nota > 7:
            raise ValidationError('La nota debe estar entre 0 y 7.')
        return nota



class ObservacionForm(forms.ModelForm):
    alumno = forms.ModelChoiceField(queryset=Alumno.objects.none(), label='Alumno')  # Inicialmente vacío

    class Meta:
        model = Observacion
        fields = ['alumno', 'contenido', 'fecha']  # Asegúrate de incluir el campo de alumno
        widgets = {
            'contenido': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Escribe aquí la observación...'}),
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'contenido': 'Contenido de la Observación',
            'fecha': 'Fecha',
        }

    def __init__(self, *args, **kwargs):
        super(ObservacionForm, self).__init__(*args, **kwargs)
        self.fields['alumno'].widget.attrs.update({'class': 'form-control'})
        self.fields['fecha'].widget.attrs.update({'class': 'form-control'})
        self.fields['contenido'].widget.attrs.update({'class': 'form-control'})
    
    


class ApoderadoForm(forms.ModelForm):
    class Meta:
        model = Apoderado
        fields = ['nombre', 'apellido', 'email', 'telefono']


class AlumnoForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)  # Campo de contraseña
    
    class Meta:
        model = Alumno
        fields = ['nombre', 'apellido', 'email', 'apoderado', 'password', 'curso', 'estado_admision'] 
        widgets = {
            'curso': forms.Select(),  # Esto generará un menú desplegable para seleccionar el curso
            'apoderado': forms.Select(),  # Esto generará un menú desplegable para seleccionar el apoderado
        }
