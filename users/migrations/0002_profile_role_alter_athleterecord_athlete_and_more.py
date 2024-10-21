# Generated by Django 5.1 on 2024-09-22 21:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('Athlete', 'Atleta'), ('Coach', 'Entrenador')], default='Athlete', max_length=50),
        ),
        migrations.AlterField(
            model_name='athleterecord',
            name='athlete',
            field=models.ForeignKey(limit_choices_to={'role': 'Athlete'}, on_delete=django.db.models.deletion.CASCADE, related_name='athlete_records', to='users.profile'),
        ),
        migrations.AlterField(
            model_name='athleterecord',
            name='coach',
            field=models.ForeignKey(limit_choices_to={'role': 'Coach'}, on_delete=django.db.models.deletion.CASCADE, related_name='coach_records', to='users.profile'),
        ),
    ]