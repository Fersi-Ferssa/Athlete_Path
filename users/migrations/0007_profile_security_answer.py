# Generated by Django 5.1 on 2024-09-22 23:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_athleterecord_evaluation_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='security_answer',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
