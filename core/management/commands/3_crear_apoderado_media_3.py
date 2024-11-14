from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Apoderado, Establecimiento

class Command(BaseCommand):
    help = 'Crear apoderados desde un archivo o batch'

    def handle(self, *args, **kwargs):
        apoderados = [
            # Establecimiento 1
            {'nombre': 'Carlos', 'apellido': 'Ramírez', 'email': 'carlos.ramirez@cole1.com', 'telefono': '123456789', 'establecimiento_id': 1},
            {'nombre': 'Ana', 'apellido': 'González', 'email': 'ana.gonzalez@cole1.com', 'telefono': '987654321', 'establecimiento_id': 1},
            {'nombre': 'Luis', 'apellido': 'Pérez', 'email': 'luis.perez@cole1.com', 'telefono': '456123789', 'establecimiento_id': 1},
            {'nombre': 'Marta', 'apellido': 'López', 'email': 'marta.lopez@cole1.com', 'telefono': '321654987', 'establecimiento_id': 1},
            {'nombre': 'Sofía', 'apellido': 'Fernández', 'email': 'sofia.fernandez@cole1.com', 'telefono': '147258369', 'establecimiento_id': 1},
            {'nombre': 'Juan', 'apellido': 'Martínez', 'email': 'juan.martinez@cole1.com', 'telefono': '963852741', 'establecimiento_id': 1},
            {'nombre': 'Patricia', 'apellido': 'García', 'email': 'patricia.garcia@cole1.com', 'telefono': '741258963', 'establecimiento_id': 1},
            {'nombre': 'Ricardo', 'apellido': 'Sánchez', 'email': 'ricardo.sanchez@cole1.com', 'telefono': '852963741', 'establecimiento_id': 1},
            {'nombre': 'Lucía', 'apellido': 'Hernández', 'email': 'lucia.hernandez@cole1.com', 'telefono': '369852741', 'establecimiento_id': 1},
            {'nombre': 'Pedro', 'apellido': 'Jiménez', 'email': 'pedro.jimenez@cole1.com', 'telefono': '741369852', 'establecimiento_id': 1},
            {'nombre': 'Isabel', 'apellido': 'Ramírez', 'email': 'isabel.ramirez@cole1.com', 'telefono': '258741963', 'establecimiento_id': 1},
            {'nombre': 'José', 'apellido': 'Vázquez', 'email': 'jose.vazquez@cole1.com', 'telefono': '963147258', 'establecimiento_id': 1},

            # Establecimiento 2
            {'nombre': 'Luis', 'apellido': 'Suárez', 'email': 'luis.suarez@cole2.com', 'telefono': '234567890', 'establecimiento_id': 2},
            {'nombre': 'Carmen', 'apellido': 'Moreno', 'email': 'carmen.moreno@cole2.com', 'telefono': '987654321', 'establecimiento_id': 2},
            {'nombre': 'José', 'apellido': 'Torres', 'email': 'jose.torres@cole2.com', 'telefono': '321654987', 'establecimiento_id': 2},
            {'nombre': 'Elena', 'apellido': 'Pérez', 'email': 'elena.perez@cole2.com', 'telefono': '741258963', 'establecimiento_id': 2},
            {'nombre': 'Ricardo', 'apellido': 'García', 'email': 'ricardo.garcia@cole2.com', 'telefono': '963852741', 'establecimiento_id': 2},
            {'nombre': 'Laura', 'apellido': 'Ruiz', 'email': 'laura.ruiz@cole2.com', 'telefono': '852963741', 'establecimiento_id': 2},
            {'nombre': 'Miguel', 'apellido': 'Fernández', 'email': 'miguel.fernandez@cole2.com', 'telefono': '369852741', 'establecimiento_id': 2},
            {'nombre': 'María', 'apellido': 'Serrano', 'email': 'maria.serrano@cole2.com', 'telefono': '741369852', 'establecimiento_id': 2},
            {'nombre': 'José', 'apellido': 'Jiménez', 'email': 'jose.jimenez@cole2.com', 'telefono': '741258963', 'establecimiento_id': 2},
            {'nombre': 'Raúl', 'apellido': 'González', 'email': 'raul.gonzalez@cole2.com', 'telefono': '963147258', 'establecimiento_id': 2},
            {'nombre': 'Teresa', 'apellido': 'Martínez', 'email': 'teresa.martinez@cole2.com', 'telefono': '258741963', 'establecimiento_id': 2},
            {'nombre': 'David', 'apellido': 'Álvarez', 'email': 'david.alvarez@cole2.com', 'telefono': '963258741', 'establecimiento_id': 2},

            # Establecimiento 3
            {'nombre': 'Antonio', 'apellido': 'Fernández', 'email': 'antonio.fernandez@cole3.com', 'telefono': '345678901', 'establecimiento_id': 3},
            {'nombre': 'Mónica', 'apellido': 'Gutiérrez', 'email': 'monica.gutierrez@cole3.com', 'telefono': '876543210', 'establecimiento_id': 3},
            {'nombre': 'Carlos', 'apellido': 'López', 'email': 'carlos.lopez@cole3.com', 'telefono': '123456789', 'establecimiento_id': 3},
            {'nombre': 'Beatriz', 'apellido': 'Torres', 'email': 'beatriz.torres@cole3.com', 'telefono': '987654321', 'establecimiento_id': 3},
            {'nombre': 'Raquel', 'apellido': 'Vázquez', 'email': 'raquel.vazquez@cole3.com', 'telefono': '456123789', 'establecimiento_id': 3},
            {'nombre': 'Javier', 'apellido': 'Sánchez', 'email': 'javier.sanchez@cole3.com', 'telefono': '321654987', 'establecimiento_id': 3},
            {'nombre': 'Laura', 'apellido': 'Hernández', 'email': 'laura.hernandez@cole3.com', 'telefono': '741258963', 'establecimiento_id': 3},
            {'nombre': 'Francisco', 'apellido': 'Jiménez', 'email': 'francisco.jimenez@cole3.com', 'telefono': '963852741', 'establecimiento_id': 3},
            {'nombre': 'Isabel', 'apellido': 'Moreno', 'email': 'isabel.moreno@cole3.com', 'telefono': '852963741', 'establecimiento_id': 3},
            {'nombre': 'José', 'apellido': 'Ramírez', 'email': 'jose.ramirez@cole3.com', 'telefono': '369852741', 'establecimiento_id': 3},
            {'nombre': 'Antonio', 'apellido': 'Serrano', 'email': 'antonio.serrano@cole3.com', 'telefono': '741369852', 'establecimiento_id': 3},
            {'nombre': 'Pedro', 'apellido': 'Álvarez', 'email': 'pedro.alvarez@cole3.com', 'telefono': '963147258', 'establecimiento_id': 3},
        ]

        for apoderado_data in apoderados:
            try:
                # Intentar obtener el establecimiento
                establecimiento = Establecimiento.objects.get(id=apoderado_data['establecimiento_id'])

                # Verificar si el usuario (apoderado) ya existe por email
                user = User.objects.filter(email=apoderado_data['email']).first()

                if user:
                    user.delete()  # Eliminar el usuario existente

                # Crear un nuevo usuario
                user = User.objects.create(
                    email=apoderado_data['email'],
                    username=f'{apoderado_data["nombre"]}_{apoderado_data["apellido"]}',  # Nombre de usuario único
                )
                user.set_password('@12345678')  # O cualquier otra lógica para la contraseña
                user.save()

                # Intentar crear el apoderado
                apoderado, created = Apoderado.objects.get_or_create(
                    email=apoderado_data['email'],  # Aseguramos que el email es único
                    nombre=apoderado_data['nombre'],
                    apellido=apoderado_data['apellido'],
                    telefono=apoderado_data['telefono'],
                    user=user,
                    establecimiento=establecimiento
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Apoderado creado: {apoderado.nombre} {apoderado.apellido}"))
                else:
                    self.stdout.write(self.style.SUCCESS(f"Apoderado ya existía: {apoderado.nombre} {apoderado.apellido}"))

            except Establecimiento.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Establecimiento con id {apoderado_data["establecimiento_id"]} no encontrado'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error al crear apoderado: {str(e)}'))
