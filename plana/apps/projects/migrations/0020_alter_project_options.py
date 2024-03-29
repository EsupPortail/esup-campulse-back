# Generated by Django 3.2.19 on 2023-06-01 09:27

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0019_alter_projectcomment_project'),
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
                ],
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
            },
        ),
    ]
