from django import forms
from .models import Asistencia, Alumno, Calificacion, Observacion, Apoderado, Curso, InformeFinanciero, Contrato, CursoAlumno, Establecimiento
from django.core.exceptions import ValidationError
from django_select2.forms import Select2MultipleWidget
from django.contrib.auth.models import User


class AsistenciaForm(forms.ModelForm):
    establecimiento = forms.ModelChoiceField(
        queryset=Establecimiento.objects.all(),
        required=True,
        label="Establecimiento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Asistencia
        fields = ['curso', 'fecha', 'establecimiento']  # Agregado 'establecimiento'

    # Agregar campos dinámicamente para los alumnos
    def __init__(self, *args, **kwargs):
        establecimiento = kwargs.pop('establecimiento', None)
        super().__init__(*args, **kwargs)

        # Filtrar los alumnos según el establecimiento proporcionado
        if establecimiento:
            alumnos = Alumno.objects.filter(establecimiento=establecimiento)
        else:
            alumnos = Alumno.objects.none()  # Si no hay establecimiento, no mostrar alumnos

        # Crear campos de asistencia para cada alumno
        for alumno in alumnos:
            self.fields[f'presente_{alumno.id}'] = forms.BooleanField(
                required=False,
                label=f'{alumno.nombre} {alumno.apellido} presente'
            )
            self.fields[f'ausente_{alumno.id}'] = forms.BooleanField(
                required=False,
                label=f'{alumno.nombre} {alumno.apellido} ausente'
            )
            self.fields[f'justificado_{alumno.id}'] = forms.BooleanField(
                required=False,
                label=f'{alumno.nombre} {alumno.apellido} justificado'
            )


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
    password = forms.CharField(widget=forms.PasswordInput)
    cursos = forms.ModelMultipleChoiceField(
        queryset=Curso.objects.none(),  # Inicialmente no hay cursos
        widget=Select2MultipleWidget(attrs={'class': 'CursoAlumno'}),  # Usando el widget Select2
        required=True,
        label="Cursos"
    )
    apoderado = forms.ModelChoiceField(
        queryset=Apoderado.objects.none(),  # Inicialmente no hay apoderados
        required=True,
        label="Apoderado"
    )
    establecimiento_nombre = forms.CharField(
        label='Establecimiento',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        required=True
    )

    class Meta:
        model = Alumno
        fields = ['nombre', 'apellido', 'email', 'apoderado', 'password', 'estado_admision']

        ESTADO_ADMISION_CHOICES = [
            ('Aprobado', 'Aprobado'),
            ('Pendiente', 'Pendiente'),
        ]

        widgets = {
            'apoderado': forms.Select(),
            'estado_admision': forms.Select(choices=ESTADO_ADMISION_CHOICES),
        }

    def __init__(self, *args, **kwargs):
        # Obtener el establecimiento desde kwargs
        self.establecimiento_instance = kwargs.pop('establecimiento_instance', None)
        alumno_instance = kwargs.get('instance')

        super().__init__(*args, **kwargs)

        # Filtrar los cursos asociados con el establecimiento relacionado
        if self.establecimiento_instance:
            self.fields['cursos'].queryset = Curso.objects.filter(establecimiento=self.establecimiento_instance)
            self.fields['apoderado'].queryset = Apoderado.objects.filter(establecimiento=self.establecimiento_instance)

        # Si se proporciona un establecimiento, mostrar su nombre como solo lectura
        if self.establecimiento_instance:
            self.fields['establecimiento_nombre'].initial = self.establecimiento_instance.nombre

        if alumno_instance:
            # Asignar cursos en los que el alumno está inscrito si ya existe una instancia de alumno
            self.fields['cursos'].initial = [curso_alumno.curso for curso_alumno in alumno_instance.curso_alumno_relacion.all()]

    def save(self, commit=True):
        alumno = super().save(commit=False)
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']

        # Obtener o crear el usuario basado en el email
        user, created = User.objects.get_or_create(username=email)
        user.set_password(password)
        user.save()

        alumno.user = user  # Asociar el usuario con el alumno

        # Asignar el establecimiento al alumno si se pasó como argumento
        if self.establecimiento_instance:
            alumno.establecimiento = self.establecimiento_instance

        if commit:
            alumno.save()

        # Guardar la relación ManyToMany entre el alumno y los cursos
        selected_cursos = self.cleaned_data['cursos']
        alumno.curso_alumno_relacion.clear()  # Limpiar cursos actuales para evitar duplicados
        for curso in selected_cursos:
            CursoAlumno.objects.get_or_create(alumno=alumno, curso=curso)

        return alumno


    
class InformeFinancieroForm(forms.ModelForm):
    class Meta:
        model = InformeFinanciero
        fields = ['concepto', 'monto', 'observaciones']



class ContratoForm(forms.ModelForm):
    # Mantener el campo valor_total como solo lectura
    valor_total = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label='Valor Total',
        initial=1500000,  # Valor predeterminado
        widget=forms.NumberInput(attrs={'readonly': 'readonly'})  # Solo lectura
    )

    # Limitar las opciones de forma_pago
    FORMA_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('cheque', 'Cheque'),
    ]
    
    forma_pago = forms.ChoiceField(
        choices=FORMA_PAGO_CHOICES,
        initial='efectivo',
        label='Forma de Pago'
    )

    # Campo de fecha
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'placeholder': 'YYYY-MM-DD', 'type': 'date'}),
        input_formats=['%Y-%m-%d'],
        label='Fecha'
    )

    # Campo oculto para el ID del alumno
    alumno_id = forms.IntegerField(widget=forms.HiddenInput())

    # Mostrar el nombre y apellido del alumno en solo lectura
    alumno_nombre = forms.CharField(
        label='Alumno',
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    # Campo oculto para el ID del apoderado
    apoderado_id = forms.IntegerField(widget=forms.HiddenInput())

    # Mostrar el nombre y apellido del apoderado en solo lectura
    apoderado_nombre = forms.CharField(
        label='Apoderado',
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    # Campo oculto para el ID del establecimiento
    establecimiento_id = forms.IntegerField(widget=forms.HiddenInput())

    # Mostrar el nombre del establecimiento en solo lectura
    establecimiento_nombre = forms.CharField(
        label='Establecimiento',
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    class Meta:
        model = Contrato
        fields = [
            'alumno_id', 'alumno_nombre', 'apoderado_id', 'apoderado_nombre',
            'establecimiento_id', 'establecimiento_nombre', 'fecha', 'valor_total', 'forma_pago', 'observaciones'
        ]
    
    def __init__(self, *args, **kwargs):
        alumno_instance = kwargs.pop('alumno_instance', None)
        apoderado_instance = kwargs.pop('apoderado_instance', None)
        establecimiento_instance = kwargs.pop('establecimiento_instance', None)
        super(ContratoForm, self).__init__(*args, **kwargs)

        if alumno_instance:
            self.fields['alumno_id'].initial = alumno_instance.id  # Guardar el ID del alumno
            self.fields['alumno_nombre'].initial = f"{alumno_instance.nombre} {alumno_instance.apellido}"  # Mostrar nombre completo
        
        if apoderado_instance:
            self.fields['apoderado_id'].initial = apoderado_instance.id  # Asignar el ID del apoderado
            self.fields['apoderado_nombre'].initial = f"{apoderado_instance.nombre} {apoderado_instance.apellido}"  # Mostrar nombre completo del apoderado
        
        if establecimiento_instance:
            self.fields['establecimiento_id'].initial = establecimiento_instance.id  # Guardar el ID del establecimiento
            self.fields['establecimiento_nombre'].initial = establecimiento_instance.nombre  # Mostrar nombre del establecimiento

