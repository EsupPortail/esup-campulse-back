# Generated by Django 3.2.16 on 2023-05-03 07:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0015_auto_20230418_1443'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentupload',
            name='document_upload_status',
        ),
        migrations.AlterField(
            model_name='document',
            name='process_type',
            field=models.CharField(
                choices=[
                    ('CHARTER_ASSOCIATION', 'Charter for Association'),
                    ('CHARTER_PROJECT_COMMISSION', 'Charter for Project Commission'),
                    ('DOCUMENT_ASSOCIATION', 'Document for Association'),
                    ('DOCUMENT_USER', 'Document for User'),
                    ('DOCUMENT_PROJECT', 'Document for Project'),
                    ('DOCUMENT_PROJECT_REVIEW', 'Document for Project Review'),
                    ('NO_PROCESS', 'Document not linked to a process'),
                ],
                default='NO_PROCESS',
                max_length=32,
                verbose_name='Document Status',
            ),
        ),
    ]