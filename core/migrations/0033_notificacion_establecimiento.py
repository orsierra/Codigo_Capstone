# Generated by Django 5.1.3 on 2024-11-14 00:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_merge_0027_subdirector_0031_merge_20241106_1902'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificacion',
            name='establecimiento',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='notificaciones', to='core.establecimiento'),
        ),
    ]
