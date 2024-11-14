from django.core.management.base import BaseCommand
from core.models import Curso, Profesor, Establecimiento
from datetime import time

class Command(BaseCommand):
    help = 'Crea cursos con niveles, asignaturas y asigna profesores existentes a cada curso.'

    def handle(self, *args, **options):
        niveles = ["1ero medio", "2do medio", "3ero medio", "4to medio"]
        asignaturas = [
            "Lenguaje", "Biología", "Química", "Física", "Matemáticas",
            "Historia", "Ed física", "Artes visuales", "Música"
        ]
        
        establecimientos = Establecimiento.objects.all()
        
        hora_inicial = time(8, 0)  # Hora inicial para los cursos

        for establecimiento in establecimientos:
            for nivel in niveles:
                for asignatura in asignaturas:
                    # Generar el nombre del curso
                    nombre_curso = f"{nivel} - {asignatura}"

                    # Buscar si ya existe un curso con el mismo nombre y establecimiento
                    curso_existente = Curso.objects.filter(establecimiento=establecimiento, nombre=nombre_curso).first()

                    if curso_existente:
                        # Si el curso ya existe, lo mostramos en la salida
                        self.stdout.write(self.style.SUCCESS(f"Curso ya existe: {curso_existente.nombre} en {curso_existente.establecimiento.nombre}"))
                    else:
                        # Buscar un profesor que coincida con la asignatura y el establecimiento
                        profesor = Profesor.objects.filter(asignatura=asignatura, establecimiento=establecimiento).first()
                        
                        if profesor:
                            # Crear el curso solo si se encuentra un profesor
                            curso = Curso.objects.create(
                                establecimiento=establecimiento,
                                nombre=nombre_curso,
                                asignatura=asignatura,
                                profesor=profesor,
                                dias="Lunes a Viernes",
                                hora=hora_inicial,  # Especificar una hora aquí
                                sala=f"Sala {nivel}"  # Asignar el nombre de la sala como "Sala <nivel>"
                            )
                            self.stdout.write(self.style.SUCCESS(f"Curso creado: {curso.nombre} en {curso.establecimiento.nombre}"))
                        else:
                            self.stdout.write(self.style.WARNING(f"Sin profesor para: {nombre_curso} en {establecimiento.nombre}"))
        
        self.stdout.write(self.style.SUCCESS("Creación de cursos completada."))
