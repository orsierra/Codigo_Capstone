from django.core.management.base import BaseCommand
from core.models import AsisMatricula, AsisFinanza, Establecimiento
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Crear tres usuarias de AsisMatricula y AsisFinanza, una para cada establecimiento'

    def handle(self, *args, **kwargs):
        # Suponiendo que ya existen tres establecimientos en la base de datos
        establecimientos = Establecimiento.objects.all()[:3]

        # Datos de las tres usuarias de AsisMatricula
        usuarias_matricula_data = [
            {'nombre': 'Laura', 'apellido': 'Díaz', 'username': 'laura_diaz'},
            {'nombre': 'Marta', 'apellido': 'Ramírez', 'username': 'marta_ramirez'},
            {'nombre': 'Sofía', 'apellido': 'López', 'username': 'sofia_lopez'},
        ]

        # Crear usuarias de AsisMatricula
        for i, establecimiento in enumerate(establecimientos):
            data = usuarias_matricula_data[i]
            
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
            
            # Crear la instancia de AsisMatricula
            AsisMatricula.objects.get_or_create(
                user=user,
                establecimiento=establecimiento,
                nombre=data['nombre'],
                apellido=data['apellido'],
                email=email
            )

        # Datos de las tres usuarias de AsisFinanza
        usuarias_finanza_data = [
            {'nombre': 'Ana', 'apellido': 'Pérez', 'username': 'ana_perez'},
            {'nombre': 'Beatriz', 'apellido': 'González', 'username': 'beatriz_gonzalez'},
            {'nombre': 'Claudia', 'apellido': 'Martínez', 'username': 'claudia_martinez'},
        ]

        # Crear usuarias de AsisFinanza
        for i, establecimiento in enumerate(establecimientos):
            data = usuarias_finanza_data[i]
            
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
            
            # Crear la instancia de AsisFinanza
            AsisFinanza.objects.get_or_create(
                user=user,
                establecimiento=establecimiento,
                nombre=data['nombre'],
                apellido=data['apellido'],
                email=email
            )

        self.stdout.write(self.style.SUCCESS('Tres usuarias de AsisMatricula y AsisFinanza creadas exitosamente.'))
