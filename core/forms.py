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
    valor_total = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label='Valor Total',
        initial=1500000,  # Establece el valor predeterminado en 1500000
        widget=forms.NumberInput(attrs={'readonly': 'readonly'})  # Mantener como solo lectura
    )

    # Limitar las opciones de forma_pago
    FORMA_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('cheque', 'Cheque'),
    ]
    
    forma_pago = forms.ChoiceField(choices=FORMA_PAGO_CHOICES, initial='efectivo')

    # Cambiar el campo fecha a DateField
    fecha = forms.DateField(
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM-DD'}),
        input_formats=['%Y-%m-%d'],  # Formato que acepta el input
        label='Fecha'
    )

    # Campo oculto para el ID del alumno
    alumno_id = forms.IntegerField(widget=forms.HiddenInput())
    
    # Mostrar el nombre y apellido del alumno pero que sea solo lectura
    alumno_nombre = forms.CharField(
        label='Alumno',
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    # Campo oculto para el ID del apoderado
    apoderado_id = forms.IntegerField(widget=forms.HiddenInput())

    # Mostrar el nombre y apellido del apoderado pero que sea solo lectura
    apoderado_nombre = forms.CharField(
        label='Apoderado',
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    class Meta:
        model = Contrato
        fields = ['alumno_id', 'alumno_nombre', 'apoderado_id', 'apoderado_nombre', 'fecha', 'valor_total', 'forma_pago', 'observaciones']

    def __init__(self, *args, **kwargs):
        alumno_instance = kwargs.pop('alumno_instance', None)
        apoderado_instance = kwargs.pop('apoderado_instance', None)
        super(ContratoForm, self).__init__(*args, **kwargs)

        if alumno_instance:
            self.fields['alumno_id'].initial = alumno_instance.id  # Guardar el ID del alumno
            self.fields['alumno_nombre'].initial = f"{alumno_instance.nombre} {alumno_instance.apellido}"  # Mostrar nombre completo
        
        if apoderado_instance:
            # Asignamos el id del apoderado al campo oculto
            self.fields['apoderado_id'].initial = apoderado_instance.id
            # Mostramos el nombre y apellido del apoderado en el campo de solo lectura
            self.fields['apoderado_nombre'].initial = f"{apoderado_instance.nombre} {apoderado_instance.apellido}"




