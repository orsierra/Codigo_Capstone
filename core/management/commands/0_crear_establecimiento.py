from django.core.management.base import BaseCommand
from core.models import Establecimiento

class Command(BaseCommand):
    help = 'Crear o actualizar registros de establecimientos en la base de datos'

    def handle(self, *args, **kwargs):
        # Crear o actualizar los establecimientos
        establecimientos_data = [
            {
                'id': 1,
                'nombre': "Colegio Nuevos Horizontes",
                'direccion': "Calle Principal 123",
                'telefono': "123456789",
                'email': "info@nuevoshorizontes.com"
            },
            {
                'id': 2,
                'nombre': "Colegio Nuevos Horizontes 2",
                'direccion': "Avenida Secundaria 456",
                'telefono': "987654321",
                'email': "contacto@nuevoshorizontes2.com"
            },
            {
                'id': 3,
                'nombre': "Colegio Nuevos Horizontes 3",
                'direccion': "Camino Tercero 789",
                'telefono': "111222333",
                'email': "info@nuevoshorizontes3.com"
            }
        ]

        for establecimiento in establecimientos_data:
            # Usamos update_or_create para crear o actualizar
            obj, created = Establecimiento.objects.update_or_create(
                id=establecimiento['id'],
                defaults=establecimiento
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Establecimiento {obj.nombre} creado con éxito.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Establecimiento {obj.nombre} actualizado con éxito.'))
