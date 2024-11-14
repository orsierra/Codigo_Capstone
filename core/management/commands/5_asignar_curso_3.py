from django.core.management.base import BaseCommand
from core.models import Establecimiento, Alumno, Curso, CursoAlumno

class Command(BaseCommand):
    help = 'Contar los alumnos y asignarlos a los cursos en tres establecimientos'

    def handle(self, *args, **kwargs):
        try:
            # Obtener los tres establecimientos
            establecimientos = Establecimiento.objects.filter(id__in=[1, 2, 3])

            for establecimiento in establecimientos:
                # Obtener todos los alumnos asociados al establecimiento
                alumnos = Alumno.objects.filter(apoderado__establecimiento=establecimiento)

                # Contar el total de alumnos
                total_alumnos = alumnos.count()
                self.stdout.write(self.style.SUCCESS(f'Total de alumnos en el establecimiento {establecimiento.nombre}: {total_alumnos}'))

                # Dividir el total de alumnos en 4 grupos
                alumnos_por_grupo = total_alumnos // 4  # Dividimos los alumnos entre 4

                # Dividir los alumnos en 4 grupos
                grupo_1 = alumnos[:alumnos_por_grupo]
                grupo_2 = alumnos[alumnos_por_grupo:alumnos_por_grupo * 2]
                grupo_3 = alumnos[alumnos_por_grupo * 2:alumnos_por_grupo * 3]
                grupo_4 = alumnos[alumnos_por_grupo * 3:]

                self.stdout.write(self.style.SUCCESS(f'Grupo 1: {len(grupo_1)} alumnos'))
                self.stdout.write(self.style.SUCCESS(f'Grupo 2: {len(grupo_2)} alumnos'))
                self.stdout.write(self.style.SUCCESS(f'Grupo 3: {len(grupo_3)} alumnos'))
                self.stdout.write(self.style.SUCCESS(f'Grupo 4: {len(grupo_4)} alumnos'))

                # Obtener los cursos por nivel
                cursos_1ero_medio = Curso.objects.filter(nombre__startswith="1ero medio -")
                cursos_2do_medio = Curso.objects.filter(nombre__startswith="2do medio -")
                cursos_3ro_medio = Curso.objects.filter(nombre__startswith="3ero medio -")
                cursos_4to_medio = Curso.objects.filter(nombre__startswith="4to medio -")

                # Asignar alumnos de 1ero medio a los cursos de 1ero medio
                for alumno in grupo_1:
                    for curso in cursos_1ero_medio:
                        # Verificar si la asociación ya existe antes de crearla
                        if not CursoAlumno.objects.filter(alumno=alumno, curso=curso).exists():
                            CursoAlumno.objects.create(alumno=alumno, curso=curso)

                # Asignar alumnos de 2do medio a los cursos de 2do medio
                for alumno in grupo_2:
                    for curso in cursos_2do_medio:
                        # Verificar si la asociación ya existe antes de crearla
                        if not CursoAlumno.objects.filter(alumno=alumno, curso=curso).exists():
                            CursoAlumno.objects.create(alumno=alumno, curso=curso)

                # Asignar alumnos de 3ero medio a los cursos de 3ero medio
                for alumno in grupo_3:
                    for curso in cursos_3ro_medio:
                        # Verificar si la asociación ya existe antes de crearla
                        if not CursoAlumno.objects.filter(alumno=alumno, curso=curso).exists():
                            CursoAlumno.objects.create(alumno=alumno, curso=curso)

                # Asignar alumnos de 4to medio a los cursos de 4to medio
                for alumno in grupo_4:
                    for curso in cursos_4to_medio:
                        # Verificar si la asociación ya existe antes de crearla
                        if not CursoAlumno.objects.filter(alumno=alumno, curso=curso).exists():
                            CursoAlumno.objects.create(alumno=alumno, curso=curso)

                self.stdout.write(self.style.SUCCESS(f'Los alumnos del establecimiento {establecimiento.nombre} han sido asignados correctamente a los cursos'))

        except Establecimiento.DoesNotExist:
            self.stdout.write(self.style.ERROR('Uno o más establecimientos no encontrados'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al asignar alumnos: {str(e)}'))
