from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from core.models import Curso, Profesor
from django.utils import timezone
from datetime import time

class Command(BaseCommand):
    help = 'Crea cursos para cada nivel con las asignaturas y los relaciona con los profesores correspondientes'

    def handle(self, *args, **kwargs):
        # Datos de los niveles y asignaturas
        niveles = ["1ero medio", "2do medio", "3ero medio", "4to medio"]
        asignaturas = [
            "Lenguaje", "Biología", "Química", "Física", "Matemáticas",
            "Historia", "Ed física", "Artes visuales", "Música"
        ]
        
        # Datos de los profesores
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
        
        # Crear profesores si no existen
        for prof_data in profesores_data:
            # Create or get the user first
            user, created_user = User.objects.get_or_create(
                username=prof_data['email'],  # Use email as username
                defaults={
                    'email': prof_data['email'],
                    'first_name': prof_data['nombre'],
                    'last_name': prof_data['apellido']
                }
            )

            # Establecer la contraseña
            user.set_password('@12345678')  # Establecer la contraseña
            user.save()  # Guardar el usuario

            # Ahora crear o obtener el profesor
            profesor, created_prof = Profesor.objects.get_or_create(
                user=user,  # Vincular al usuario creado
                defaults={'asignatura': prof_data['asignatura']}
            )
            
            if created_prof:
                self.stdout.write(self.style.SUCCESS(f'Profesor creado: {profesor.nombre} {profesor.apellido}'))
            else:
                self.stdout.write(self.style.WARNING(f'Profesor ya existe: {profesor.nombre} {profesor.apellido}'))

        # Crear cursos para cada nivel y asignatura
        for nivel in niveles:
            for asignatura in asignaturas:
                # Buscar al profesor de la asignatura correspondiente
                profesor = Profesor.objects.filter(asignatura=asignatura).first()
                if not profesor:
                    self.stdout.write(self.style.ERROR(f"No se encontró un profesor para la asignatura {asignatura}"))
                    continue

                # Crear curso
                curso, created = Curso.objects.get_or_create(
                    nombre=f"{nivel} - {asignatura}",
                    asignatura=asignatura,
                    profesor=profesor,
                    defaults={
                        'dias': 'Lunes y Miércoles',  # Ejemplo de días de clase
                        'hora': time(8, 0),          # Hora ejemplo
                        'sala': 'Sala por asignar'
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Curso creado: {curso.nombre} para {asignatura}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Curso ya existe: {curso.nombre}'))
        
        self.stdout.write(self.style.SUCCESS("Comando completado con éxito"))
