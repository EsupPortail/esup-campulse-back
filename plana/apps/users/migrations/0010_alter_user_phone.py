# Generated by Django 3.2.16 on 2022-11-16 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_auto_20221114_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(default='', max_length=32, null=True, verbose_name='Téléphone'),
        ),
    ]
