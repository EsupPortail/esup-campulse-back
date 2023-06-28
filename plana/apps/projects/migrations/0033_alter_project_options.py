# Generated by Django 3.2.16 on 2023-06-26 14:18

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0032_alter_project_project_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={
                'permissions': [
                    ('add_project_association', 'Can add a project as an association.'),
                    ('add_project_user', 'Can add a project as a user.'),
                    (
                        'change_project_as_bearer',
                        'Can update project fields filled by bearer (student).',
                    ),
                    (
                        'change_project_as_validator',
                        'Can update project fields filled by validator (manager).',
                    ),
                    ('view_project_any_fund', 'Can view all projects for a fund.'),
                    (
                        'view_project_any_institution',
                        'Can view all projects for an institution.',
                    ),
                    (
                        'view_project_any_status',
                        'Can view all projects without status limit.',
                    ),
                ],
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
            },
        ),
    ]