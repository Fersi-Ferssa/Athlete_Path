# Generated by Django 5.1 on 2024-09-22 22:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_profile_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='athleterecord',
            name='evaluation_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]