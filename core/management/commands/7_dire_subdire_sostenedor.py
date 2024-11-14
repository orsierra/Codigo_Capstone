from django.core.management.base import BaseCommand
from core.models import Director, Subdirector, Sostenedor, Establecimiento
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crear directores, subdirectores y un único sostenedor'

    def handle(self, *args, **kwargs):
        # Crear directores para los tres establecimientos
        establecimientos = Establecimiento.objects.all()[:3]

        # Datos de los tres directores
        directores_data = [
            {'nombre': 'Juan', 'apellido': 'Pérez', 'username': 'juan_perez'},
            {'nombre': 'Carlos', 'apellido': 'Sánchez', 'username': 'carlos_sanchez'},
            {'nombre': 'Mónica', 'apellido': 'Gómez', 'username': 'monica_gomez'},
        ]

        for i, establecimiento in enumerate(establecimientos):
            data = directores_data[i]
            
            # El email será igual al username
            email = data['username'] + '@example.com'
            
            # Crear un usuario de Django
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={'email': email, 'first_name': data['nombre'], 'last_name': data['apellido']}
            )
            
            if created:
                user.set_password('@12345678')  # Establece una contraseña predeterminada
                user.save()
            
            # Crear la instancia de Director
            Director.objects.get_or_create(
                user=user,
                establecimiento=establecimiento,
                nombre=data['nombre'],
                apellido=data['apellido'],
                email=email
            )

        self.stdout.write(self.style.SUCCESS('Directores creados exitosamente para cada establecimiento.'))

        # Crear subdirectores para los tres establecimientos
        subdirectores_data = [
            {'nombre': 'Pedro', 'apellido': 'Martínez', 'username': 'pedro_martinez'},
            {'nombre': 'Luis', 'apellido': 'Fernández', 'username': 'luis_fernandez'},
            {'nombre': 'Raquel', 'apellido': 'Hernández', 'username': 'raquel_hernandez'},
        ]

        for i, establecimiento in enumerate(establecimientos):
            data = subdirectores_data[i]
            
            # El email será igual al username
            email = data['username'] + '@example.com'
            
            # Crear un usuario de Django
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={'email': email, 'first_name': data['nombre'], 'last_name': data['apellido']}
            )
            
            if created:
                user.set_password('@12345678')  # Establece una contraseña predeterminada
                user.save()
            
            # Crear la instancia de Subdirector
            Subdirector.objects.get_or_create(
                user=user,
                establecimiento=establecimiento,
                nombre=data['nombre'],
                apellido=data['apellido'],
                email=email
            )

        self.stdout.write(self.style.SUCCESS('Subdirectores creados exitosamente para cada establecimiento.'))

        # Crear un único sostenedor
        datos_sostenedor = {
            'nombre': 'Carlos',
            'apellido': 'Gómez',
            'username': 'carlos_gomez',
            'email': 'carlos_gomez@example.com',
            'telefono': '123456789'
        }

        # Crear el usuario de Django
        user, created = User.objects.get_or_create(
            username=datos_sostenedor['username'],
            defaults={
                'email': datos_sostenedor['email'],
                'first_name': datos_sostenedor['nombre'],
                'last_name': datos_sostenedor['apellido'],
            }
        )
        
        if created:
            # Establecer la contraseña del usuario
            user.set_password('@12345678')
            user.save()

        # Crear la instancia de Sostenedor
        Sostenedor.objects.get_or_create(
            user=user,
            nombre=datos_sostenedor['nombre'],
            apellido=datos_sostenedor['apellido'],
            email=datos_sostenedor['email'],
            telefono=datos_sostenedor['telefono']
        )

        self.stdout.write(self.style.SUCCESS('Sostenedor creado exitosamente.'))
