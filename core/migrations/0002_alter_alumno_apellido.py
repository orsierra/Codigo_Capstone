# Generated by Django 5.1.1 on 2024-10-13 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumno',
            name='apellido',
            field=models.CharField(max_length=200),
        ),
    ]
