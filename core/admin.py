from django.contrib import admin
from .models import Profesor, Curso

# Registro del modelo Profesor
admin.site.register(Profesor)

# Configuración del modelo Curso en el admin
@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'asignatura', 'profesor', 'dias', 'hora')
    list_filter = ('profesor', 'asignatura')
    search_fields = ('nombre', 'profesor__nombre')
