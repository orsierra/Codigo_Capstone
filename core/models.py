# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Apoderado(models.Model):
    id_apoderado = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=50)
    direccion = models.CharField(max_length=70)
    corrreo = models.CharField(max_length=60)
    telefono = models.CharField(max_length=15)
    relacion_con_estudiante = models.CharField(max_length=15)
    contrasena = models.CharField(max_length=20)

    class Meta:
        managed = True
        db_table = 'apoderado'


class Asignatura(models.Model):
    id_asignatura = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=40)
    nivel = models.CharField(max_length=40)
    grado = models.CharField(max_length=40)
    area = models.CharField(max_length=40)

    class Meta:
        managed = True
        db_table = 'asignatura'


class Asistencia(models.Model):
    id_asistencia = models.IntegerField(primary_key=True)
    presente = models.BooleanField()
    justificativo = models.CharField(max_length=50)
    clase_id_clase = models.ForeignKey('Clase', models.DO_NOTHING, db_column='clase_id_clase')

    class Meta:
        managed = True
        db_table = 'asistencia'


class Cargaacademica(models.Model):
    id_carga_academica = models.IntegerField(primary_key=True)
    horas_semanales = models.IntegerField()
    profesor_id_profesor = models.OneToOneField('Profesor', models.DO_NOTHING, db_column='profesor_id_profesor', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cargaacademica'


class Clase(models.Model):
    id_clase = models.IntegerField(primary_key=True)
    fecha_clase = models.DateField()
    hora_inicio = models.DateTimeField()
    hora_fin = models.DateTimeField()
    tema = models.CharField(max_length=70)
    observacion = models.CharField(max_length=300)

    class Meta:
        managed = True
        db_table = 'clase'


class Contrato(models.Model):
    id_contrato = models.IntegerField(primary_key=True)
    fecha_firma = models.DateField()
    valor_total = models.IntegerField()
    forma_pago = models.CharField(max_length=20)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    apoderado_id_apoderado = models.ForeignKey(Apoderado, models.DO_NOTHING, db_column='apoderado_id_apoderado')

    class Meta:
        managed = True
        db_table = 'contrato'


class Curso(models.Model):
    id_curso = models.IntegerField(primary_key=True)
    nivel = models.CharField(max_length=40)
    grado = models.CharField(max_length=15)
    seccion = models.CharField(max_length=15)
    año_lectivo = models.DateField()
    estudiante_id_estudiante = models.OneToOneField('Estudiante', models.DO_NOTHING, db_column='estudiante_id_estudiante', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'curso'


class Director(models.Model):
    id_director = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    apellido = models.CharField(max_length=30)
    establecimiento_id_establecimiento = models.OneToOneField('Establecimiento', models.DO_NOTHING, db_column='establecimiento_id_establecimiento', blank=True, null=True)
    contrasena = models.CharField(max_length=20)

    class Meta:
        managed = True
        db_table = 'director'



class Empleado(models.Model):
    id_empleado = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=100)
    correo = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    apellido = models.CharField(max_length=100)
    cargo = models.CharField(max_length=30)
    establecimiento_id_establecimiento = models.ForeignKey('Establecimiento', models.DO_NOTHING, db_column='establecimiento_id_establecimiento', blank=True, null=True)  
    contrasena = models.CharField(max_length=20)

    class Meta:
        managed = True
        db_table = 'empleado'


class Establecimiento(models.Model):
    id_establecimiento = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)
    email = models.CharField(max_length=60)
    estudiante_id_estudiante = models.OneToOneField('Estudiante', models.DO_NOTHING, db_column='estudiante_id_estudiante', blank=True, null=True)
    director_id_director = models.OneToOneField(Director, models.DO_NOTHING, db_column='director_id_director', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'establecimiento'


class Estudiante(models.Model):
    id_estudiante = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=20)
    apellido = models.CharField(max_length=30)
    fecha_nacimiento = models.DateField()
    direccion = models.CharField(max_length=50)
    genero = models.CharField(max_length=15)
    curso_id_curso = models.OneToOneField(Curso, models.DO_NOTHING, db_column='curso_id_curso', blank=True, null=True)
    examen_inicial_id_examen = models.OneToOneField('ExamenInicial', models.DO_NOTHING, db_column='examen_inicial_id_examen', blank=True, null=True)
    establecimiento_id_establecimiento = models.OneToOneField(Establecimiento, models.DO_NOTHING, db_column='establecimiento_id_establecimiento', blank=True, null=True) 
    correo = models.CharField(max_length=150)
    contrasena = models.CharField(max_length=20)
    apoderado_id_apoderado = models.ForeignKey(Apoderado, models.DO_NOTHING, db_column='apoderado_id_apoderado', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'estudiante'


class Evaluacion(models.Model):
    id_evaluacion = models.IntegerField(primary_key=True)
    tipo_evaluacion = models.CharField(max_length=100)
    nota = models.FloatField()
    asignatura_id_asignatura = models.ForeignKey(Asignatura, models.DO_NOTHING, db_column='asignatura_id_asignatura', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'evaluacion'


class ExamenInicial(models.Model):
    id_examen = models.IntegerField(primary_key=True)
    fecha_examen = models.DateField()
    nota = models.FloatField()
    estudiante_id_estudiante = models.OneToOneField(Estudiante, models.DO_NOTHING, db_column='estudiante_id_estudiante', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'examen_inicial'


class Informeacademico(models.Model):
    id_informe_academico = models.IntegerField(primary_key=True)
    periodo = models.CharField(max_length=50)
    fecha_emision = models.DateField()
    promedio = models.FloatField()
    observacion = models.CharField(max_length=400)
    estudiante_id_estudiante = models.ForeignKey(Estudiante, models.DO_NOTHING, db_column='estudiante_id_estudiante', blank=True, null=True)
    periodoacademico_id_periodo_academico = models.ForeignKey('Periodoacademico', models.DO_NOTHING, db_column='periodoacademico_id_periodo_academico', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'informeacademico'


class Informefinanza(models.Model):
    id_informe_finanza = models.IntegerField(primary_key=True)
    saldo = models.IntegerField()
    fecha_emision = models.DateField()
    descripcion = models.CharField(max_length=100)
    contrato_id_contrato = models.ForeignKey(Contrato, models.DO_NOTHING, db_column='contrato_id_contrato', blank=True, null=True)
    apoderado_id_apoderado = models.ForeignKey(Apoderado, models.DO_NOTHING, db_column='apoderado_id_apoderado', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'informefinanza'


class Matricula(models.Model):
    id_matricula = models.IntegerField(primary_key=True)
    año_lectivo = models.DateField()
    fecha_solicitud = models.DateField()
    fecha_confirmacion = models.DateField()
    estado = models.CharField(max_length=20)
    estudiante_id_estudiante = models.ForeignKey(Estudiante, models.DO_NOTHING, db_column='estudiante_id_estudiante', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'matricula'


class Observacion(models.Model):
    id_observacion = models.IntegerField(primary_key=True)
    observacion = models.CharField(max_length=500)
    estudiante_id_estudiante = models.ForeignKey(Estudiante, models.DO_NOTHING, db_column='estudiante_id_estudiante', blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'observacion'


class Periodoacademico(models.Model):
    id_periodo_academico = models.IntegerField(primary_key=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=15)

    class Meta:
        managed = True
        db_table = 'periodoacademico'


class Profesor(models.Model):
    id_profesor = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=40)
    apellido = models.CharField(max_length=50)
    título = models.CharField(max_length=60)
    area = models.CharField(max_length=30)
    cargaacademica_id_carga_academica = models.OneToOneField(Cargaacademica, models.DO_NOTHING, db_column='cargaacademica_id_carga_academica', blank=True, null=True)    
    establecimiento_id_establecimiento = models.ForeignKey(Establecimiento, models.DO_NOTHING, db_column='establecimiento_id_establecimiento', blank=True, null=True)    
    correo = models.CharField(max_length=150)
    contrasena = models.CharField(max_length=20)

    class Meta:
        managed = True
        db_table = 'profesor'


class RelacionCursoAsignatura(models.Model):
    curso_id_curso = models.OneToOneField(Curso, models.DO_NOTHING, db_column='curso_id_curso', primary_key=True)  # The composite primary key (curso_id_curso, asignatura_id_asignatura) found, that is not supported. The first column is selected.
    asignatura_id_asignatura = models.ForeignKey(Asignatura, models.DO_NOTHING, db_column='asignatura_id_asignatura')

    class Meta:
        managed = True
        db_table = 'relacion_curso_asignatura'
        unique_together = (('curso_id_curso', 'asignatura_id_asignatura'),)


class RelacionCursoClase(models.Model):
    curso_id_curso = models.OneToOneField(Curso, models.DO_NOTHING, db_column='curso_id_curso', primary_key=True)  # The composite primary key (curso_id_curso, clase_id_clase) found, that is not supported. The first column is selected.
    clase_id_clase = models.ForeignKey(Clase, models.DO_NOTHING, db_column='clase_id_clase')

    class Meta:
        managed = True
        db_table = 'relacion_curso_clase'
        unique_together = (('curso_id_curso', 'clase_id_clase'),)


class RelacionCursoProfesor(models.Model):
    curso_id_curso = models.OneToOneField(Curso, models.DO_NOTHING, db_column='curso_id_curso', primary_key=True)  # The composite primary key (curso_id_curso, profesor_id_profesor) found, that is not supported. The first column is selected.
    profesor_id_profesor = models.ForeignKey(Profesor, models.DO_NOTHING, db_column='profesor_id_profesor')

    class Meta:
        managed = True
        db_table = 'relacion_curso_profesor'
        unique_together = (('curso_id_curso', 'profesor_id_profesor'),)


class RelacionCursoSala(models.Model):
    curso_id_curso = models.OneToOneField(Curso, models.DO_NOTHING, db_column='curso_id_curso', primary_key=True)  # The composite primary key (curso_id_curso, sala_id_sala) found, that is not supported. The first column is selected.
    sala_id_sala = models.ForeignKey('Sala', models.DO_NOTHING, db_column='sala_id_sala')

    class Meta:
        managed = True
        db_table = 'relacion_curso_sala'
        unique_together = (('curso_id_curso', 'sala_id_sala'),)


class Respaldoacademico(models.Model):
    id_respaldo_academico = models.IntegerField(primary_key=True)
    fecha_respaldo = models.DateField()
    descripcion = models.CharField(max_length=30)
    periodoacademico_id_periodo_academico = models.ForeignKey(Periodoacademico, models.DO_NOTHING, db_column='periodoacademico_id_periodo_academico')

    class Meta:
        managed = True
        db_table = 'respaldoacademico'


class Sala(models.Model):
    id_sala = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=50)
    capacidad = models.CharField(max_length=10)
    tipo = models.CharField(max_length=30)
    establecimiento_id_establecimiento = models.ForeignKey(Establecimiento, models.DO_NOTHING, db_column='establecimiento_id_establecimiento')

    class Meta:
        managed = True
        db_table = 'sala'


class Tarea(models.Model):
    id_tarea = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=150)
    fecha_entrega = models.DateField()
    clase_id_clase = models.ForeignKey(Clase, models.DO_NOTHING, db_column='clase_id_clase')

    class Meta:
        managed = True
        db_table = 'tarea'