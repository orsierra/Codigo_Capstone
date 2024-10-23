# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone



# modelo profesor, apoderado y alumno

class Profesor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Apoderado(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=200, default='Sin apellido')
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Alumno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=200, default='Sin apellido')
    email = models.EmailField(unique=True)
    apoderado = models.ForeignKey(Apoderado, related_name='alumnos', on_delete=models.SET_NULL, null=True)
    estado_admision = models.CharField(max_length=50, default='Pendiente')
    curso = models.ForeignKey('Curso', related_name='alumnos_inscritos', on_delete=models.SET_NULL, null=True)


    def __str__(self):
        return f"{self.nombre} {self.apellido}"



#Modulo curso relacionado con alumno
class Curso(models.Model): 
    nombre = models.CharField(max_length=100)
    asignatura = models.CharField(max_length=100)
    profesor = models.ForeignKey('Profesor', on_delete=models.CASCADE)  
    alumnos = models.ManyToManyField('Alumno', blank=True, related_name='cursos_asignados')  # Cadena para evitar circular
    dias = models.CharField(max_length=100)
    hora = models.TimeField()
    sala = models.CharField(max_length=50, default='Sala por asignar')

    def __str__(self):
        return self.nombre


#===============================================================================================
#MODULOS DE LIBRO DE CLASES CON PROFESOR
# modelo ASISTENCIA, se relaciona con el libro de clases del profe
class Asistencia(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha = models.DateField()
    alumnos_presentes = models.ManyToManyField('Alumno', related_name='asistencias_presentes', blank=True)
    alumnos_ausentes = models.ManyToManyField('Alumno', related_name='asistencias_ausentes', blank=True)
    alumnos_justificados = models.ManyToManyField('Alumno', related_name='asistencias_justificados', blank=True)

    def __str__(self):
        return f"Asistencia para {self.curso} el {self.fecha}"



#modelo CALIFICACION, se relaciona con el libro de clases del profe
class Calificacion(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)
    nota = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Calificación de {self.alumno} en {self.curso}: {self.nota}"

    def is_valid_nota(self):
        return 0 <= self.nota <= 7  # se valida que la nota ingresada por el profesor sea entre 0 y 7

#=====================================================================================================================

class RegistroAcademico(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE)
    fecha = models.DateField()
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Registro académico de {self.alumno} en {self.curso}"


class Informe(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha = models.DateField()
    contenido = models.TextField()

    def __str__(self):
        return f"Informe de {self.curso} para {self.fecha}"


class Observacion(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE)
    fecha = models.DateField()
    contenido = models.TextField()

    def __str__(self):
        return f"Observación de {self.alumno} en {self.curso} el {self.fecha}"
    
#==============================================================================================

class InformeFinanciero(models.Model):
    concepto = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.concepto

class InformeAcademico(models.Model):
    total_alumnos = models.IntegerField()
    promedio_notas = models.DecimalField(max_digits=5, decimal_places=2)
    promedio_asistencia = models.DecimalField(max_digits=5, decimal_places=2)
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE)

    def __str__(self):
        return f'Informe de {self.curso.nombre}'