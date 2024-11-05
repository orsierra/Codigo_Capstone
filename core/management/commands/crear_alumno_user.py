from django.contrib.auth.models import User
from core.models import Apoderado, Alumno  # Asegúrate de cambiar 'core' por el nombre real de tu aplicación
from django.utils.crypto import get_random_string

# Crear una lista de los datos de los apoderados
apoderados_data = [
    {'nombre': 'Luis', 'apellido': 'Díaz', 'email': 'luis.diaz@cole.com', 'telefono': '123456789', 'user_id': 6},
    {'nombre': 'María', 'apellido': 'Fernández', 'email': 'maria.fernandez@cole.com', 'telefono': '987654321', 'user_id': 7},
    {'nombre': 'María', 'apellido': 'Martínez', 'email': 'maria.gonzalez@cole.com', 'telefono': '987654321', 'user_id': 21},
    {'nombre': 'Carlos', 'apellido': 'Vergara', 'email': 'carlos.sanchez@cole.com', 'telefono': '456789123', 'user_id': 22},
    {'nombre': 'Laura', 'apellido': 'Fernandez', 'email': 'laura.martinez@cole.com', 'telefono': '321654987', 'user_id': 23},
    {'nombre': 'Javier', 'apellido': 'Sierra', 'email': 'javier.hernandez@cole.com', 'telefono': '654123789', 'user_id': 24},
    {'nombre': 'Ana', 'apellido': 'Díaz', 'email': 'ana.lopez@cole.com', 'telefono': '789123456', 'user_id': 25},
    {'nombre': 'Fernando', 'apellido': 'Ray', 'email': 'fernando.ramirez@cole.com', 'telefono': '852963741', 'user_id': 26},
    {'nombre': 'Patricia', 'apellido': 'Almiray', 'email': 'patricia.torres@cole.com', 'telefono': '147258369', 'user_id': 27},
    {'nombre': 'Ricardo', 'apellido': 'Almiray', 'email': 'ricardo.vazquez@cole.com', 'telefono': '963852741', 'user_id': 28},
]

# Crear los alumnos correspondientes
alumnos_data = [
    {'nombre': 'Juan', 'apellido': 'Díaz', 'email': 'juan.diaz@cole.com', 'apoderado_user_id': 6},
    {'nombre': 'Sofía', 'apellido': 'Fernández', 'email': 'sofia.fernandez@cole.com', 'apoderado_user_id': 7},
    {'nombre': 'Diego', 'apellido': 'Martínez', 'email': 'diego.martinez@cole.com', 'apoderado_user_id': 21},
    {'nombre': 'Camila', 'apellido': 'Vergara', 'email': 'camila.vergara@cole.com', 'apoderado_user_id': 22},
    {'nombre': 'Mateo', 'apellido': 'Fernandez', 'email': 'mateo.fernandez@cole.com', 'apoderado_user_id': 23},
    {'nombre': 'Valentina', 'apellido': 'Sierra', 'email': 'valentina.sierra@cole.com', 'apoderado_user_id': 24},
    {'nombre': 'Lucas', 'apellido': 'Díaz', 'email': 'lucas.diaz@cole.com', 'apoderado_user_id': 25},
    {'nombre': 'Isabella', 'apellido': 'Ray', 'email': 'isabella.ray@cole.com', 'apoderado_user_id': 26},
    {'nombre': 'Natalia', 'apellido': 'Almiray', 'email': 'natalia.almiray@cole.com', 'apoderado_user_id': 27},
    {'nombre': 'Gonzalo', 'apellido': 'Almiray', 'email': 'gonzalo.almiray@cole.com', 'apoderado_user_id': 28},
]

# Crear los alumnos y sus usuarios en la base de datos
for alumno_data in alumnos_data:
    apoderado = Apoderado.objects.get(user_id=alumno_data['apoderado_user_id'])  # Obtener el apoderado
    
    # Establecer una contraseña fija
    password = "@12345678"  # Contraseña fija que deseas usar
    
    # Crear el usuario
    user = User.objects.create_user(
        username=alumno_data['email'],  # Puedes usar el email como username
        password=password,
        email=alumno_data['email'],
        first_name=alumno_data['nombre'],
        last_name=apoderado.apellido  # Usar el apellido del apoderado
    )
    
    # Crear el alumno asociado al usuario
    alumno = Alumno.objects.create(
        user=user,  # Asociar el usuario creado
        nombre=alumno_data['nombre'],
        apellido=apoderado.apellido,  # Apellido igual al del apoderado
        email=alumno_data['email'],
        apoderado=apoderado,
        estado_admision='Aprobado',
        curso=None  # Si deseas asignar un curso, debes tenerlo previamente creado
    )
    
    print(f"Alumno {alumno} creado con apoderado {apoderado}. Contraseña: {password}")
