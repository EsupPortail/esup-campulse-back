# Generated by Django 3.2.20 on 2023-07-18 09:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0036_alter_project_project_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectcommissionfund',
            name='is_validated_by_admin',
            field=models.BooleanField(
                default=None, null=True, verbose_name='Is validated by admin'
            ),
        ),
    ]