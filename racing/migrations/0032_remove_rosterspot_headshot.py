# Generated by Django 5.1.2 on 2024-11-17 18:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('racing', '0031_race_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rosterspot',
            name='headshot',
        ),
    ]
