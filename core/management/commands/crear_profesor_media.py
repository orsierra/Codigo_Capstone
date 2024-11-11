from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Profesor  

class Command(BaseCommand):
    help = 'Agrega profesores a la base de datos con asignaturas específicas'

    def handle(self, *args, **kwargs):
        # Datos de los profesores (nombre, apellido, email y asignatura)
        profesores_data = [
            {"nombre": "Juan", "apellido": "Pérez", "email": "prof.len@cole.com", "asignatura": "Lenguaje"},
            {"nombre": "Ana", "apellido": "Gómez", "email": "prof.bio@cole.com", "asignatura": "Biología"},
            {"nombre": "Carlos", "apellido": "Sánchez", "email": "prof.qui@cole.com", "asignatura": "Química"},
            {"nombre": "María", "apellido": "Martínez", "email": "prof.fis@cole.com", "asignatura": "Física"},
            {"nombre": "Luis", "apellido": "Ramírez", "email": "prof.mat@cole.com", "asignatura": "Matemáticas"},
            {"nombre": "Elena", "apellido": "Fernández", "email": "prof.his@cole.com", "asignatura": "Historia"},
            {"nombre": "Pedro", "apellido": "López", "email": "prof.edf@cole.com", "asignatura": "Ed física"},
            {"nombre": "Laura", "apellido": "Rodríguez", "email": "prof.art@cole.com", "asignatura": "Artes visuales"},
            {"nombre": "Marta", "apellido": "Díaz", "email": "prof.mus@cole.com", "asignatura": "Música"},
        ]

        # Crear instancias de usuario y profesor para cada asignatura
        for profesor_data in profesores_data:
            # Verificar si el usuario ya existe
            if User.objects.filter(email=profesor_data["email"]).exists():
                self.stdout.write(self.style.WARNING(f'El usuario {profesor_data["email"]} ya existe.'))
                continue

            # Crear un usuario para el profesor
            user = User.objects.create_user(
                username=profesor_data["email"],
                email=profesor_data["email"],
                password="@12345678"  # Cambia esta contraseña a una segura
            )

            # Crear una instancia de Profesor y asociarla con el usuario creado
            Profesor.objects.create(
                user=user,
                nombre=profesor_data["nombre"],
                apellido=profesor_data["apellido"],
                email=profesor_data["email"],
                asignatura=profesor_data["asignatura"]
            )

            self.stdout.write(self.style.SUCCESS(f'Profesor {profesor_data["nombre"]} {profesor_data["apellido"]} agregado con éxito.'))
