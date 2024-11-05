from django.core.management.base import BaseCommand
from core.models import Alumno, Curso, CursoAlumno

class Command(BaseCommand):
    help = 'Asigna alumnos al curso 1ero medio'

    def handle(self, *args, **options):
        # Datos de los alumnos
        alumnos_data = [
            {'nombre': 'Juan', 'apellido': 'Díaz', 'email': 'juan.diaz@example.com', 'apoderado_user_id': 6},
            {'nombre': 'Sofía', 'apellido': 'Fernández', 'email': 'sofia.fernandez@example.com', 'apoderado_user_id': 7},
            {'nombre': 'Diego', 'apellido': 'Martínez', 'email': 'diego.martinez@example.com', 'apoderado_user_id': 21},
            {'nombre': 'Camila', 'apellido': 'Vergara', 'email': 'camila.vergara@example.com', 'apoderado_user_id': 22},
            {'nombre': 'Mateo', 'apellido': 'Fernandez', 'email': 'mateo.fernandez@example.com', 'apoderado_user_id': 23},
            {'nombre': 'Valentina', 'apellido': 'Sierra', 'email': 'valentina.sierra@example.com', 'apoderado_user_id': 24},
            {'nombre': 'Lucas', 'apellido': 'Díaz', 'email': 'lucas.diaz@example.com', 'apoderado_user_id': 25},
            {'nombre': 'Isabella', 'apellido': 'Ray', 'email': 'isabella.ray@example.com', 'apoderado_user_id': 26},
            {'nombre': 'Natalia', 'apellido': 'Almiray', 'email': 'natalia.almiray@example.com', 'apoderado_user_id': 27},
            {'nombre': 'Gonzalo', 'apellido': 'Almiray', 'email': 'gonzalo.almiray@example.com', 'apoderado_user_id': 28},
        ]

        # Intenta obtener el curso 1ero medio
        curso_1ero = Curso.objects.filter(nombre__startswith='1ero medio -').first()

        if curso_1ero is None:
            self.stdout.write(self.style.ERROR('No se encontró el curso "1ero medio -".'))
            return
        
        for alumno_data in alumnos_data:
            # Crear o actualizar el alumno
            alumno, created = Alumno.objects.get_or_create(
                email=alumno_data['email'],  # Usa el email como identificador único
                defaults={
                    'nombre': alumno_data['nombre'],
                    'apellido': alumno_data['apellido'],
                    'apoderado_user_id': alumno_data['apoderado_user_id'],
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f'Alumno {alumno.nombre} {alumno.apellido} creado.'))
            else:
                self.stdout.write(self.style.WARNING(f'El alumno {alumno.nombre} {alumno.apellido} ya existe.'))

            # Asignar el alumno al curso
            curso_alumno, created = CursoAlumno.objects.get_or_create(alumno=alumno, curso=curso_1ero)

            if created:
                self.stdout.write(self.style.SUCCESS(f'Alumno {alumno.nombre} asignado al curso {curso_1ero.nombre}.'))
            else:
                self.stdout.write(self.style.WARNING(f'El alumno {alumno.nombre} ya estaba asignado al curso {curso_1ero.nombre}.'))
