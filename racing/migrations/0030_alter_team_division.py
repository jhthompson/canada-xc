# Generated by Django 5.1.2 on 2024-11-13 02:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('racing', '0029_officialresult_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='division',
            field=models.CharField(choices=[('USPORTS', 'U Sports'), ('CLUB', 'Club'), ('HS', 'High School')], default='CLUB', max_length=10),
        ),
    ]
