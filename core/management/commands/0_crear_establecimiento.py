from django.core.management.base import BaseCommand
from core.models import Establecimiento

class Command(BaseCommand):
    help = 'Crear registros de establecimientos en la base de datos si no existen'

    def handle(self, *args, **kwargs):
        # Crear los establecimientos solo si no existen
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
            # Usamos get_or_create para evitar duplicados
            obj, created = Establecimiento.objects.get_or_create(
                id=establecimiento['id'],
                defaults=establecimiento
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Establecimiento {obj.nombre} creado con éxito.'))
            else:
                self.stdout.write(self.style.WARNING(f'El establecimiento {obj.nombre} ya existe.'))

