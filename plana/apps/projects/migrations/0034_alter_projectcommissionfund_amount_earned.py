# Generated by Django 3.2.16 on 2023-06-27 12:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0033_alter_project_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectcommissionfund',
            name='amount_earned',
            field=models.PositiveIntegerField(
                default=None, verbose_name='Amount earned'
            ),
        ),
    ]
