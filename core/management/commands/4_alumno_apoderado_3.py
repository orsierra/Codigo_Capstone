from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Establecimiento, Apoderado, Alumno

class Command(BaseCommand):
    help = 'Crea alumnos, apoderados y los relaciona con el establecimiento'

    def handle(self, *args, **kwargs):
        # Establecimiento con id = 1
        establecimiento = Establecimiento.objects.get(id=1)

        # Datos de los apoderados y alumnos para el establecimiento 1
        relacionados = [
            {'apoderado': 'Carlos Ramírez', 'alumno': 'Andrea Ramírez'},
            {'apoderado': 'Ana González', 'alumno': 'Miguel García'},
            {'apoderado': 'Luis Pérez', 'alumno': 'Sara Fernández'},
            {'apoderado': 'Marta López', 'alumno': 'Diego Martínez'},
            {'apoderado': 'Sofía Fernández', 'alumno': 'Luciana López'},
            {'apoderado': 'Juan Martínez', 'alumno': 'Javier Sánchez'},
            {'apoderado': 'Patricia García', 'alumno': 'Valeria Pérez'},
            {'apoderado': 'Ricardo Sánchez', 'alumno': 'Emilio Díaz'},
            {'apoderado': 'Lucía Hernández', 'alumno': 'Paula Ruiz'},
            {'apoderado': 'Pedro Jiménez', 'alumno': 'Sebastián Castro'},
            {'apoderado': 'Isabel Ramírez', 'alumno': 'Camila Gómez'},
            {'apoderado': 'José Vázquez', 'alumno': 'Rodrigo Martínez'},
            {'apoderado': 'Marta López', 'alumno': 'Daniela Suárez'},
            {'apoderado': 'Sofía Fernández', 'alumno': 'Álvaro Ruiz'},
            {'apoderado': 'Juan Martínez', 'alumno': 'Nadia García'},
            {'apoderado': 'Patricia García', 'alumno': 'Santiago Fernández'},
            {'apoderado': 'Ricardo Sánchez', 'alumno': 'Julieta López'},
            {'apoderado': 'Lucía Hernández', 'alumno': 'Nicolás Sánchez'},
            {'apoderado': 'Pedro Jiménez', 'alumno': 'Elena Rodríguez'},
            {'apoderado': 'Isabel Ramírez', 'alumno': 'Gabriel Pérez'},
            {'apoderado': 'José Vázquez', 'alumno': 'Marcela Gómez'},
            {'apoderado': 'Marta López', 'alumno': 'Tomás Jiménez'},
            {'apoderado': 'Sofía Fernández', 'alumno': 'Mariana Ramírez'},
            {'apoderado': 'Juan Martínez', 'alumno': 'Fernando Sánchez'}
        ]

        for relacion in relacionados:
            # Buscar apoderado por nombre y apellido
            apoderado_nombre, apoderado_apellido = relacion['apoderado'].split()
            try:
                apoderado = Apoderado.objects.get(
                    nombre=apoderado_nombre,
                    apellido=apoderado_apellido,
                    establecimiento=establecimiento
                )
                self.stdout.write(self.style.SUCCESS(f'Apoderado {apoderado_nombre} {apoderado_apellido} encontrado'))
            except Apoderado.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Apoderado {apoderado_nombre} {apoderado_apellido} no encontrado, saltando...'))
                continue

            alumno_nombre, alumno_apellido = relacion['alumno'].split()
            email_alumno = f'{alumno_nombre.lower()}.{alumno_apellido.lower()}@colealumno.com'

            if Alumno.objects.filter(email=email_alumno).exists():
                self.stdout.write(self.style.WARNING(f'Alumno con email {email_alumno} ya existe, saltando creación...'))
                continue

            username_base = f'{alumno_nombre.lower()}.{alumno_apellido.lower()}'
            username = username_base
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f'{username_base}{counter}'
                counter += 1

            user_alumno = User.objects.create_user(username=username, password='@12345678')

            alumno = Alumno.objects.create(
                user=user_alumno,
                nombre=alumno_nombre,
                apellido=alumno_apellido,
                email=email_alumno,
                apoderado=apoderado,
                establecimiento=establecimiento,
                estado_admision="Aprobado" 

            )

            self.stdout.write(self.style.SUCCESS(f'Alumno {alumno_nombre} {alumno_apellido} creado con éxito'))

        # Apoderados y alumnos del establecimiento 2
        establecimiento_2 = Establecimiento.objects.get(id=2)
        relacionados_2 = relacionados_2 = [
            {'apoderado': 'Luis Suárez', 'alumno': 'María Suárez'},
            {'apoderado': 'Luis Suárez', 'alumno': 'Carlos Suárez'},
            {'apoderado': 'Carmen Moreno', 'alumno': 'José Moreno'},
            {'apoderado': 'Carmen Moreno', 'alumno': 'Ana Moreno'},
            {'apoderado': 'José Torres', 'alumno': 'Elena Torres'},
            {'apoderado': 'José Torres', 'alumno': 'Carlos Torres'},
            {'apoderado': 'Elena Pérez', 'alumno': 'Ricardo Pérez'},
            {'apoderado': 'Elena Pérez', 'alumno': 'Marta Pérez'},
            {'apoderado': 'Ricardo García', 'alumno': 'David García'},
            {'apoderado': 'Ricardo García', 'alumno': 'Luis García'},
            {'apoderado': 'Laura Ruiz', 'alumno': 'José Ruiz'},
            {'apoderado': 'Laura Ruiz', 'alumno': 'Sara Ruiz'},
            {'apoderado': 'Miguel Fernández', 'alumno': 'Carlos Fernández'},
            {'apoderado': 'Miguel Fernández', 'alumno': 'José Fernández'},
            {'apoderado': 'María Serrano', 'alumno': 'Raúl Serrano'},
            {'apoderado': 'María Serrano', 'alumno': 'Ana Serrano'},
            {'apoderado': 'José Jiménez', 'alumno': 'Sofía Jiménez'},
            {'apoderado': 'José Jiménez', 'alumno': 'Antonio Jiménez'},
            {'apoderado': 'Raúl González', 'alumno': 'Juan González'},
            {'apoderado': 'Raúl González', 'alumno': 'Marta González'},
            {'apoderado': 'Teresa Martínez', 'alumno': 'Antonio Martínez'},
            {'apoderado': 'Teresa Martínez', 'alumno': 'José Martínez'},
            {'apoderado': 'David Álvarez', 'alumno': 'Sara Álvarez'},
            {'apoderado': 'David Álvarez', 'alumno': 'Ricardo Álvarez'}
        ]
        for relacion in relacionados_2:
            apoderado_nombre, apoderado_apellido = relacion['apoderado'].split()
            try:
                apoderado = Apoderado.objects.get(
                    nombre=apoderado_nombre,
                    apellido=apoderado_apellido,
                    establecimiento=establecimiento_2
                )
                self.stdout.write(self.style.SUCCESS(f'Apoderado {apoderado_nombre} {apoderado_apellido} encontrado en Establecimiento 2'))
            except Apoderado.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Apoderado {apoderado_nombre} {apoderado_apellido} no encontrado en Establecimiento 2, saltando...'))
                continue

            alumno_nombre, alumno_apellido = relacion['alumno'].split()
            email_alumno = f'{alumno_nombre.lower()}.{alumno_apellido.lower()}@colealumno.com'

            if Alumno.objects.filter(email=email_alumno).exists():
                self.stdout.write(self.style.WARNING(f'Alumno con email {email_alumno} ya existe en Establecimiento 2, saltando creación...'))
                continue

            username_base = f'{alumno_nombre.lower()}.{alumno_apellido.lower()}'
            username = username_base
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f'{username_base}{counter}'
                counter += 1

            user_alumno = User.objects.create_user(username=username, password='@12345678')

            alumno = Alumno.objects.create(
                user=user_alumno,
                nombre=alumno_nombre,
                apellido=alumno_apellido,
                email=email_alumno,
                apoderado=apoderado,
                establecimiento=establecimiento_2,
                estado_admision="Aprobado" 
            )

            self.stdout.write(self.style.SUCCESS(f'Alumno {alumno_nombre} {alumno_apellido} creado con éxito en Establecimiento 2'))


        # Similar bucle de creación para establecimiento 2

        # Apoderados y alumnos del establecimiento 3
        establecimiento_3 = Establecimiento.objects.get(id=3)
        relacionados_3 = [
            {'apoderado': 'Antonio Fernández', 'alumno': 'Lucas Fernández'},
            {'apoderado': 'Antonio Fernández', 'alumno': 'Elena Fernández'},
            {'apoderado': 'Mónica Gutiérrez', 'alumno': 'Paula Gutiérrez'},
            {'apoderado': 'Mónica Gutiérrez', 'alumno': 'Diego Gutiérrez'},
            {'apoderado': 'Carlos López', 'alumno': 'Ana López'},
            {'apoderado': 'Carlos López', 'alumno': 'Luis López'},
            {'apoderado': 'Beatriz Torres', 'alumno': 'Sofía Torres'},
            {'apoderado': 'Beatriz Torres', 'alumno': 'Mateo Torres'},
            {'apoderado': 'Raquel Vázquez', 'alumno': 'Martín Vázquez'},
            {'apoderado': 'Raquel Vázquez', 'alumno': 'Gabriela Vázquez'},
            {'apoderado': 'Javier Sánchez', 'alumno': 'Marcos Sánchez'},
            {'apoderado': 'Javier Sánchez', 'alumno': 'Daniela Sánchez'},
            {'apoderado': 'Laura Hernández', 'alumno': 'Isabel Hernández'},
            {'apoderado': 'Laura Hernández', 'alumno': 'Javier Hernández'},
            {'apoderado': 'Francisco Jiménez', 'alumno': 'Carlos Jiménez'},
            {'apoderado': 'Francisco Jiménez', 'alumno': 'Lucía Jiménez'},
            {'apoderado': 'Isabel Moreno', 'alumno': 'Ricardo Moreno'},
            {'apoderado': 'Isabel Moreno', 'alumno': 'Valeria Moreno'},
            {'apoderado': 'José Ramírez', 'alumno': 'Diego Ramírez'},
            {'apoderado': 'José Ramírez', 'alumno': 'Andrea Ramírez'},
            {'apoderado': 'Antonio Serrano', 'alumno': 'Lucía Serrano'},
            {'apoderado': 'Antonio Serrano', 'alumno': 'Nicolás Serrano'},
            {'apoderado': 'Pedro Álvarez', 'alumno': 'Sara Álvarez'},
            {'apoderado': 'Pedro Álvarez', 'alumno': 'Tomás Álvarez'}
        ]

        for relacion in relacionados_3:
            apoderado_nombre, apoderado_apellido = relacion['apoderado'].split()
            try:
                apoderado = Apoderado.objects.get(
                    nombre=apoderado_nombre,
                    apellido=apoderado_apellido,
                    establecimiento=establecimiento_3
                )
                self.stdout.write(self.style.SUCCESS(f'Apoderado {apoderado_nombre} {apoderado_apellido} encontrado en Establecimiento 3'))
            except Apoderado.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Apoderado {apoderado_nombre} {apoderado_apellido} no encontrado en Establecimiento 3, saltando...'))
                continue

            alumno_nombre, alumno_apellido = relacion['alumno'].split()
            email_alumno = f'{alumno_nombre.lower()}.{alumno_apellido.lower()}@colealumno.com'

            if Alumno.objects.filter(email=email_alumno).exists():
                self.stdout.write(self.style.WARNING(f'Alumno con email {email_alumno} ya existe en Establecimiento 3, saltando creación...'))
                continue

            username_base = f'{alumno_nombre.lower()}.{alumno_apellido.lower()}'
            username = username_base
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f'{username_base}{counter}'
                counter += 1

            user_alumno = User.objects.create_user(username=username, password='@12345678')

            alumno = Alumno.objects.create(
                user=user_alumno,
                nombre=alumno_nombre,
                apellido=alumno_apellido,
                email=email_alumno,
                apoderado=apoderado,
                establecimiento=establecimiento_3,
                estado_admision="Aprobado" 
            )

            self.stdout.write(self.style.SUCCESS(f'Alumno {alumno_nombre} {alumno_apellido} creado con éxito en Establecimiento 3'))
