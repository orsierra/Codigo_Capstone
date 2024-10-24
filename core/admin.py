from django.contrib import admin
from .models import Profesor, Curso, Alumno, Apoderado, Asistencia, Calificacion, InformeFinanciero

# Registro del modelo Profesor
admin.site.register(Profesor)
admin.site.register(Alumno)
admin.site.register(Apoderado)
admin.site.register(Asistencia)
admin.site.register(Calificacion)
admin.site.register(InformeFinanciero)

# Configuración del modelo Curso en el admin
@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'asignatura', 'profesor', 'dias', 'hora')
    list_filter = ('profesor', 'asignatura')
    search_fields = ('nombre', 'profesor__nombre')
