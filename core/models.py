from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



# modelo profesor, apoderado y alumno
# Nuevo modelo de Establecimiento
class Establecimiento(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre



# Nuevo modelo de Establecimiento
class Establecimiento(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# Modelo Profesor
class Profesor(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='profesores', null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    asignatura = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
<<<<<<< HEAD
        return f"{self.nombre} {self.apellido} - {self.establecimiento.nombre if self.establecimiento else 'Sin Establecimiento'}"
=======
        return f"{self.nombre} {self.apellido}- {self.establecimiento.nombre if self.establecimiento else 'Sin Establecimiento'}"

>>>>>>> 0a8adaebda7543fd12cebfee7af3c4a308e30ef2


# Modelo Apoderado
class Apoderado(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='apoderados', null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=200, default='Sin apellido')
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.establecimiento.nombre if self.establecimiento else 'Sin Establecimiento'}"
<<<<<<< HEAD
=======

class Notificacion(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='notificaciones', null=True, blank=True)
    apoderado = models.ForeignKey(Apoderado, on_delete=models.CASCADE)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=100, choices=[('calificacion_baja', 'Calificación Baja'), ('asistencia', 'Asistencia')], default='calificacion_baja')
    prioridad = models.IntegerField(default=1)  # Valores bajos = mayor prioridad

>>>>>>> 0a8adaebda7543fd12cebfee7af3c4a308e30ef2


# Modelo Alumno
class Alumno(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='alumnos', null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=200, default='Sin apellido')
    email = models.EmailField(unique=True)
    apoderado = models.ForeignKey(Apoderado, related_name='alumnos', on_delete=models.SET_NULL, null=True)
    estado_admision = models.CharField(max_length=50, default='Pendiente')

    def __str__(self):
<<<<<<< HEAD
        return f"{self.nombre} {self.apellido} - {self.establecimiento.nombre if self.establecimiento else 'Sin Establecimiento'}"


# Modelo Director
class Director(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='directores', null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
=======
        return f"{self.nombre} {self.apellido}- {self.establecimiento.nombre if self.establecimiento else 'Sin Establecimiento'}"
    
class Director(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='directores', null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Asociación con el modelo User de Django
>>>>>>> 0a8adaebda7543fd12cebfee7af3c4a308e30ef2
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=200, default='Sin apellido')
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.establecimiento.nombre if self.establecimiento else 'Sin Establecimiento'}"
<<<<<<< HEAD
    
# Modelo SUBDirector
class Subdirector(models.Model):
    # Relación uno a uno con el modelo de usuario para manejo de autenticación
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    
    # Relación con Establecimiento, asumiendo que el subdirector pertenece a un establecimiento
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='subdirectores')

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.establecimiento.nombre}"


# Modelo Curso
class Curso(models.Model): 
=======



#Modulo curso relacionado con alumno
class Curso(models.Model):
>>>>>>> 0a8adaebda7543fd12cebfee7af3c4a308e30ef2
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='cursos', null=True, blank=True)
    nombre = models.CharField(max_length=100)
    asignatura = models.CharField(max_length=100)
    profesor = models.ForeignKey('Profesor', on_delete=models.CASCADE)  
    alumnos = models.ManyToManyField('Alumno', blank=True, related_name='cursos_asignados')
    dias = models.CharField(max_length=100)
    hora = models.TimeField()
    sala = models.CharField(max_length=50, default='Sala por asignar')

    def __str__(self):
        return f"{self.nombre} - {self.establecimiento.nombre if self.establecimiento else 'Sin Establecimiento'}"
<<<<<<< HEAD
=======

>>>>>>> 0a8adaebda7543fd12cebfee7af3c4a308e30ef2

# Modelo Asistencia
class Asistencia(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='asistencias', null=True, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha = models.DateField()
    alumnos_presentes = models.ManyToManyField('Alumno', related_name='asistencias_presentes', blank=True)
    alumnos_ausentes = models.ManyToManyField('Alumno', related_name='asistencias_ausentes', blank=True)
    alumnos_justificados = models.ManyToManyField('Alumno', related_name='asistencias_justificados', blank=True)

    def __str__(self):
        return f"Asistencia para {self.curso} el {self.fecha}"



# Modelo Calificacion
class Calificacion(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='calificaciones', null=True, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)
    nota = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Calificación de {self.alumno} en {self.curso}: {self.nota}"

    def is_valid_nota(self):
        return 0 <= self.nota <= 7


# Modelo Registro Academico
class RegistroAcademico(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='registros_academicos', null=True, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE)
    fecha = models.DateField()
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Registro académico de {self.alumno} en {self.curso}"


# Modelo Informe
class Informe(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='informes', null=True, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha = models.DateField()
    contenido = models.TextField()

    def __str__(self):
        return f"Informe de {self.curso} para {self.fecha}"


# Modelo Observacion
class Observacion(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='observaciones', null=True, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE)
    fecha = models.DateField()
    contenido = models.TextField()

    def __str__(self):
        return f"Observación de {self.alumno} en {self.curso} el {self.fecha}"


# Modelo Informe Financiero
class InformeFinanciero(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='informes_financieros', null=True, blank=True)
<<<<<<< HEAD
=======
    concepto = models.CharField(max_length=200)
>>>>>>> 0a8adaebda7543fd12cebfee7af3c4a308e30ef2
    concepto = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.concepto


# Modelo Informe Academico
class InformeAcademico(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='informes_academicos', null=True, blank=True)
    total_alumnos = models.IntegerField()
    promedio_notas = models.DecimalField(max_digits=5, decimal_places=2)
    promedio_asistencia = models.DecimalField(max_digits=5, decimal_places=2)
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE)

    def __str__(self):
        return f'Informe de {self.curso.nombre}'


# Modelo Contrato
class Contrato(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='contratos', null=True, blank=True)
    apoderado = models.ForeignKey(Apoderado, related_name='contratos', on_delete=models.CASCADE)
    alumno = models.OneToOneField(Alumno, related_name='contrato', on_delete=models.CASCADE, null=True)
    fecha = models.DateField()
    valor_total = models.DecimalField(max_digits=11, decimal_places=2)
    forma_pago = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True, null=True)


# Modelo Asistente de Finanzas
class AsisFinanza(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='asistentes_finanzas', null=True, blank=True)
<<<<<<< HEAD
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=200, default='Sin apellido')
    email = models.EmailField(unique=True)
=======
    user = models.OneToOneField(User, on_delete= models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=200, default='Sin apellido')
    email = models.EmailField(unique=True)
    
    def __str__(self):
        return f'{self.nombre} {self.apellido} - {self.establecimiento.nombre if self.establecimiento else "Sin Establecimiento"}'

>>>>>>> 0a8adaebda7543fd12cebfee7af3c4a308e30ef2

    def __str__(self):
        return f'{self.nombre} {self.apellido} - {self.establecimiento.nombre if self.establecimiento else "Sin Establecimiento"}'


# Modelo Asistente de Matrícula
class AsisMatricula(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='asistentes_matricula', null=True, blank=True)
<<<<<<< HEAD
    user = models.OneToOneField(User, on_delete=models.CASCADE)
=======
    user = models.OneToOneField(User, on_delete= models.CASCADE)
>>>>>>> 0a8adaebda7543fd12cebfee7af3c4a308e30ef2
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=200, default='Sin apellido')
    email = models.EmailField(unique=True)

    def __str__(self):
        return f'{self.nombre} {self.apellido} - {self.establecimiento.nombre if self.establecimiento else "Sin Establecimiento"}'

<<<<<<< HEAD
=======


class CursoAlumno(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='curso_alumno_relaciones', null=True, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.SET_NULL, related_name='curso_alumno_relacion', null=True, blank=True)
    alumno = models.ForeignKey(Alumno, on_delete=models.SET_NULL, related_name='curso_alumno_relacion', null=True, blank=True)

    class Meta:
        unique_together = ('curso', 'alumno')  # Evita duplicados para el mismo alumno en el mismo curso
        verbose_name = 'Relación Curso-Alumno'
        verbose_name_plural = 'Relaciones Curso-Alumno'

    def __str__(self):
        curso_nombre = self.curso.nombre if self.curso else "Curso no asignado"
        alumno_nombre = f"{self.alumno.nombre} {self.alumno.apellido}" if self.alumno else "Alumno no asignado"
        return f"{alumno_nombre} inscrito en {curso_nombre} - {self.establecimiento.nombre if self.establecimiento else 'Sin Establecimiento'}"



class BitacoraClase(models.Model):
    establecimiento = models.ForeignKey(Establecimiento, on_delete=models.CASCADE, related_name='bitacoras_clase', null=True, blank=True)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha = models.DateField()
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    actividades_realizadas = models.TextField()
    observaciones = models.TextField(blank=True, null=True)  # Añade este campo para las observaciones opcionales

    def __str__(self):
        return f"Bitácora de {self.curso} el {self.fecha} - {self.establecimiento.nombre if self.establecimiento else 'Sin Establecimiento'}"

>>>>>>> 0a8adaebda7543fd12cebfee7af3c4a308e30ef2
