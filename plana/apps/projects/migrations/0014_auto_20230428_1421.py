# Generated by Django 3.2.16 on 2023-04-28 12:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0013_alter_project_project_status'),
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
                    ('view_project_any_commission', 'Can view all projects.'),
                ],
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
            },
        ),
        migrations.AlterModelOptions(
            name='projectcommissiondate',
            options={
                'permissions': [
                    (
                        'change_projectcommissiondate_as_bearer',
                        'Can update bearer fields (amount asked) between a project and a commission date.',
                    ),
                    (
                        'change_projectcommissiondate_as_validator',
                        'Can update validator fields (amount earned) between a project and a commission date.',
                    ),
                    (
                        'view_projectcommissiondate_any_commission',
                        'Can view all commission dates linked to a project.',
                    ),
                ],
                'verbose_name': 'Project commission date',
                'verbose_name_plural': 'Projects commissions dates',
            },
        ),
    ]
