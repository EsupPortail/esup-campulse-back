# Generated by Django 4.2.7 on 2023-11-14 13:03

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0042_alter_project_amount_all_audience_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='budget_previous_edition',
            field=models.PositiveIntegerField(default=1, verbose_name='Budget on previous edition'),
        ),
    ]
