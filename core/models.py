# models.py
from django.db import models
from django.contrib.auth.models import User

# MODELOS DE PROFESOR Y ALUMNO

class Profesor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Relación uno a uno con User
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Alumno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=200, default='Sin apellido')
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    asignatura = models.CharField(max_length=100)  # Campo para la asignatura
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    alumnos = models.ManyToManyField('Alumno', blank=True)
    dias = models.CharField(max_length=100)  # Días en que se imparte el curso
    hora = models.TimeField()  # Hora del curso

    def __str__(self):
        return self.nombre
#===============================================================================================

# MODELOS LIBRO DE CLASE DE PROFESOR

from django.db import models

class Curso(models.Model):
    nombre = models.CharField(max_length=100)
    asignatura = models.CharField(max_length=100)  # Campo para la asignatura
    profesor = models.ForeignKey('Profesor', on_delete=models.CASCADE)
    alumnos = models.ManyToManyField('Alumno', blank=True)
    dias = models.CharField(max_length=100)  # Días en que se imparte el curso
    hora = models.TimeField()  # Hora del curso

    def __str__(self):
        return self.nombre


class Asistencia(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    fecha = models.DateField()
    alumnos_presentes = models.ManyToManyField('Alumno', related_name='asistencias', blank=True)

    def __str__(self):
        return f"Asistencia para {self.curso} el {self.fecha}"


class Calificacion(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    alumno = models.ForeignKey('Alumno', on_delete=models.CASCADE)
    fecha = models.DateField()
    nota = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Calificación de {self.alumno} en {self.curso}: {self.nota}"


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
