# Generated by Django 3.2.19 on 2023-06-02 07:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0020_alter_project_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='projectcomment',
            options={
                'permissions': [
                    (
                        'view_projectcomment_any_fund',
                        'Can view all comments linked to all projects for a fund.',
                    ),
                    (
                        'view_projectcomment_any_institution',
                        'Can view all comments linked to all projects for an institution.',
                    ),
                ],
                'verbose_name': 'Project comment',
                'verbose_name_plural': 'Projects comments',
            },
        ),
    ]
