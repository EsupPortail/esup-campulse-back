# Generated by Django 3.2.20 on 2023-08-23 08:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0037_alter_projectcommissionfund_is_validated_by_admin'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='partner_association',
            field=models.TextField(default='', verbose_name='Partner association'),
        ),
    ]
