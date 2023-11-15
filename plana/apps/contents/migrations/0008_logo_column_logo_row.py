# Generated by Django 4.2.7 on 2023-11-15 09:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contents', '0007_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='logo',
            name='column',
            field=models.PositiveIntegerField(default=1, verbose_name='Column where logo is placed in layout'),
        ),
        migrations.AddField(
            model_name='logo',
            name='row',
            field=models.PositiveIntegerField(default=1, verbose_name='Row where logo is placed in layout'),
        ),
    ]
