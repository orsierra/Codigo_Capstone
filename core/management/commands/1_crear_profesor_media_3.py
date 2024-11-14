from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from core.models import Profesor

class Command(BaseCommand):
    help = 'Popula la base de datos con profesores en diferentes establecimientos'

    def handle(self, *args, **options):
        profesores_data = [
            # Establecimiento 1
            {"nombre": "Juan", "apellido": "Pérez", "email": "prof.len@cole.com", "asignatura": "Lenguaje", "establecimiento_id": 1},
            {"nombre": "Ana", "apellido": "Gómez", "email": "prof.bio@cole.com", "asignatura": "Biología", "establecimiento_id": 1},
            {"nombre": "Carlos", "apellido": "Sánchez", "email": "prof.qui@cole.com", "asignatura": "Química", "establecimiento_id": 1},
            {"nombre": "María", "apellido": "Martínez", "email": "prof.fis@cole.com", "asignatura": "Física", "establecimiento_id": 1},
            {"nombre": "Luis", "apellido": "Ramírez", "email": "prof.mat@cole.com", "asignatura": "Matemáticas", "establecimiento_id": 1},
            {"nombre": "Elena", "apellido": "Fernández", "email": "prof.his@cole.com", "asignatura": "Historia", "establecimiento_id": 1},
            {"nombre": "Pedro", "apellido": "López", "email": "prof.edf@cole.com", "asignatura": "Ed física", "establecimiento_id": 1},
            {"nombre": "Laura", "apellido": "Rodríguez", "email": "prof.art@cole.com", "asignatura": "Artes visuales", "establecimiento_id": 1},
            {"nombre": "Marta", "apellido": "Díaz", "email": "prof.mus@cole.com", "asignatura": "Música", "establecimiento_id": 1},

            # Establecimiento 2
            {"nombre": "Juan", "apellido": "González", "email": "prof.len2@cole.com", "asignatura": "Lenguaje", "establecimiento_id": 2},
            {"nombre": "Ana", "apellido": "Vega", "email": "prof.bio2@cole.com", "asignatura": "Biología", "establecimiento_id": 2},
            {"nombre": "Carlos", "apellido": "Rodríguez", "email": "prof.qui2@cole.com", "asignatura": "Química", "establecimiento_id": 2},
            {"nombre": "María", "apellido": "Morales", "email": "prof.fis2@cole.com", "asignatura": "Física", "establecimiento_id": 2},
            {"nombre": "Luis", "apellido": "Sosa", "email": "prof.mat2@cole.com", "asignatura": "Matemáticas", "establecimiento_id": 2},
            {"nombre": "Elena", "apellido": "Gómez", "email": "prof.his2@cole.com", "asignatura": "Historia", "establecimiento_id": 2},
            {"nombre": "Pedro", "apellido": "Martínez", "email": "prof.edf2@cole.com", "asignatura": "Ed física", "establecimiento_id": 2},
            {"nombre": "Laura", "apellido": "González", "email": "prof.art2@cole.com", "asignatura": "Artes visuales", "establecimiento_id": 2},
            {"nombre": "Marta", "apellido": "Pérez", "email": "prof.mus2@cole.com", "asignatura": "Música", "establecimiento_id": 2},

            # Establecimiento 3
            {"nombre": "Juan", "apellido": "Martínez", "email": "prof.len3@cole.com", "asignatura": "Lenguaje", "establecimiento_id": 3},
            {"nombre": "Ana", "apellido": "Díaz", "email": "prof.bio3@cole.com", "asignatura": "Biología", "establecimiento_id": 3},
            {"nombre": "Carlos", "apellido": "Hernández", "email": "prof.qui3@cole.com", "asignatura": "Química", "establecimiento_id": 3},
            {"nombre": "María", "apellido": "Torres", "email": "prof.fis3@cole.com", "asignatura": "Física", "establecimiento_id": 3},
            {"nombre": "Luis", "apellido": "Jiménez", "email": "prof.mat3@cole.com", "asignatura": "Matemáticas", "establecimiento_id": 3},
            {"nombre": "Elena", "apellido": "López", "email": "prof.his3@cole.com", "asignatura": "Historia", "establecimiento_id": 3},
            {"nombre": "Pedro", "apellido": "Ramírez", "email": "prof.edf3@cole.com", "asignatura": "Ed física", "establecimiento_id": 3},
            {"nombre": "Laura", "apellido": "Sánchez", "email": "prof.art3@cole.com", "asignatura": "Artes visuales", "establecimiento_id": 3},
            {"nombre": "Marta", "apellido": "González", "email": "prof.mus3@cole.com", "asignatura": "Música", "establecimiento_id": 3},
        ]

        for data in profesores_data:
            try:
                # Crear o obtener el usuario con el email como username
                user, created_user = User.objects.get_or_create(
                    username=data['email'],  # Usa el email como nombre de usuario
                    defaults={'email': data['email']}
                )

                if created_user:
                    user.set_password("@12345678")  # Cambia la contraseña por una segura en producción
                    user.save()

                # Crear o actualizar el profesor con el usuario asignado
                profesor, created_profesor = Profesor.objects.get_or_create(
                    nombre=data['nombre'],
                    apellido=data['apellido'],
                    email=data['email'],
                    asignatura=data['asignatura'],
                    establecimiento_id=data['establecimiento_id'],
                    defaults={'user': user}  # Asigna el usuario en la creación inicial
                )

                # Si el profesor ya existía pero no tenía usuario, lo asignamos
                if not created_profesor and profesor.user is None:
                    profesor.user = user
                    profesor.save()

                # Mensajes de éxito o advertencia
                if created_profesor:
                    self.stdout.write(self.style.SUCCESS(f"Profesor creado: {data['nombre']} {data['apellido']} ({data['asignatura']})"))
                else:
                    self.stdout.write(self.style.WARNING(f"Profesor ya existe: {data['nombre']} {data['apellido']} ({data['asignatura']})"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error con el profesor {data['nombre']} {data['apellido']}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("Proceso de población de profesores completado."))
