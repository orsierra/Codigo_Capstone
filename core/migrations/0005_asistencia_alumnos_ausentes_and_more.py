# Generated by Django 5.1.1 on 2024-10-14 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_curso_sala'),
    ]

    operations = [
        migrations.AddField(
            model_name='asistencia',
            name='alumnos_ausentes',
            field=models.ManyToManyField(blank=True, related_name='asistencias_ausentes', to='core.alumno'),
        ),
        migrations.AddField(
            model_name='asistencia',
            name='alumnos_justificados',
            field=models.ManyToManyField(blank=True, related_name='asistencias_justificados', to='core.alumno'),
        ),
        migrations.AlterField(
            model_name='asistencia',
            name='alumnos_presentes',
            field=models.ManyToManyField(blank=True, related_name='asistencias_presentes', to='core.alumno'),
        ),
    ]
