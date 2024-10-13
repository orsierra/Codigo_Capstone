from django.contrib import admin
from .models import Profesor, Curso, Alumno

# Registro del modelo Profesor
admin.site.register(Profesor)
admin.site.register(Alumno)

# Configuración del modelo Curso en el admin
@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'asignatura', 'profesor', 'dias', 'hora')
    list_filter = ('profesor', 'asignatura')
    search_fields = ('nombre', 'profesor__nombre')
