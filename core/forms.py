from django import forms
from .models import Asistencia, Alumno, Calificacion, Observacion, Apoderado, Curso, InformeFinanciero, Contrato
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
        
        # Opciones para el estado de admisión
        ESTADO_ADMISION_CHOICES = [
            ('Aprobado', 'Aprobado'),
            ('Pendiente', 'Pendiente'),
        ]

        widgets = {
            'curso': forms.Select(),  # Menú desplegable para seleccionar el curso
            'apoderado': forms.Select(),  # Menú desplegable para seleccionar el apoderado
            'estado_admision': forms.Select(choices=ESTADO_ADMISION_CHOICES),  # Opciones de "Aprobado" y "Pendiente"
        }



class InformeFinancieroForm(forms.ModelForm):
    class Meta:
        model = InformeFinanciero
        fields = ['concepto', 'monto', 'observaciones']
        
        
class ContratoForm(forms.ModelForm):
    # Mantener el campo valor_total como un campo de solo lectura
    valor_total = forms.DecimalField(initial=1500000, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    # Limitar las opciones de forma_pago
    FORMA_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('cheque', 'Cheque'),
    ]
    
    forma_pago = forms.ChoiceField(choices=FORMA_PAGO_CHOICES, initial='efectivo')

    # Modificar el campo de fecha para que solo muestre años
    fecha = forms.ChoiceField(
        choices=[(year, year) for year in range(2010, 2031)],  # Ajusta el rango de años según sea necesario
        label='Año'
    )

    class Meta:
        model = Contrato
        fields = ['apoderado', 'alumno', 'fecha', 'valor_total', 'forma_pago', 'observaciones']
        