# Generated by Django 3.2.16 on 2023-03-27 12:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20230327_0835'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='project',
            options={
                'permissions': [
                    (
                        'change_project_restricted_fields',
                        'Can update projects restricted fields.',
                    ),
                    ('view_project_all', 'Can view all projects.'),
                ],
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
            },
        ),
        migrations.AlterModelOptions(
            name='projectcategory',
            options={
                'permissions': [
                    (
                        'view_projectcategory_all',
                        'Can view all categories linked to a project.',
                    )
                ],
                'verbose_name': 'Project category',
                'verbose_name_plural': 'Projects categories',
            },
        ),
        migrations.AlterModelOptions(
            name='projectcommissiondate',
            options={
                'permissions': [
                    (
                        'view_projectcommissiondate_all',
                        'Can view all commission dates linked to a project.',
                    )
                ],
                'verbose_name': 'Project commission date',
                'verbose_name_plural': 'Projects commissions dates',
            },
        ),
    ]
