# Generated by Django 3.2.16 on 2023-01-26 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('associations', '0022_alter_association_path_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='association',
            name='alt_logo',
            field=models.TextField(
                blank=True, default='', null=True, verbose_name='Logo description'
            ),
        ),
    ]
