from django.contrib import admin
from .models import Profesor, Curso, Alumno, Apoderado, Asistencia, Calificacion, InformeFinanciero, Contrato, AsisFinanza, AsisMatricula, Director, Subdirector, Sostenedor

# Registro del modelo Profesor
admin.site.register(Profesor)
admin.site.register(Alumno)
admin.site.register(Apoderado)
admin.site.register(Asistencia)
admin.site.register(Calificacion)
admin.site.register(InformeFinanciero)
admin.site.register(AsisFinanza)
admin.site.register(AsisMatricula)
admin.site.register(Director)
admin.site.register(Sostenedor)
admin.site.register(Subdirector)



# Configuración del modelo Curso en el admin  Director
@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'asignatura', 'profesor', 'dias', 'hora')
    list_filter = ('profesor', 'asignatura')
    search_fields = ('nombre', 'profesor__nombre')

class ContratoAdmin(admin.ModelAdmin):
    list_display = ('alumno', 'apoderado', 'fecha', 'valor_total', 'forma_pago')  # Muestra campos personalizados
    search_fields = ('alumno__nombre', 'apoderado__nombre')  # Permite buscar por nombre del alumno o apoderado

admin.site.register(Contrato, ContratoAdmin)
