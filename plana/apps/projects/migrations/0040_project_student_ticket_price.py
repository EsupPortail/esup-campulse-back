# Generated by Django 3.2.20 on 2023-08-31 13:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0039_project_processing_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='student_ticket_price',
            field=models.PositiveIntegerField(
                default=0, verbose_name='Amount of money asked for a student'
            ),
        ),
    ]