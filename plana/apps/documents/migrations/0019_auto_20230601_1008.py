# Generated by Django 3.2.19 on 2023-06-01 08:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0018_rename_commission_document_fund'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='document',
            options={
                'permissions': [
                    ('add_document_any_fund', 'Can add documents linked to any fund.'),
                    (
                        'add_document_any_institution',
                        'Can add documents linked to any institution.',
                    ),
                    (
                        'change_document_any_fund',
                        'Can change documents linked to any fund.',
                    ),
                    (
                        'change_document_any_institution',
                        'Can change documents linked to any institution.',
                    ),
                    (
                        'delete_document_any_fund',
                        'Can delete documents linked to any fund.',
                    ),
                    (
                        'delete_document_any_institution',
                        'Can delete documents linked to any institution.',
                    ),
                ],
                'verbose_name': 'Document',
                'verbose_name_plural': 'Documents',
            },
        ),
        migrations.AlterField(
            model_name='document',
            name='process_type',
            field=models.CharField(
                choices=[
                    ('CHARTER_ASSOCIATION', 'Charter for Association'),
                    ('CHARTER_PROJECT_FUND', 'Charter for Project Fund'),
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
