# Generated by Django 4.2.13 on 2024-05-22 09:13

from django.db import migrations, models

import plana.libs.validators


class Migration(migrations.Migration):

    dependencies = [
        ('contents', '0011_content_is_editable'),
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('setting', models.CharField(max_length=128, unique=True, verbose_name='Setting name')),
                (
                    'parameters',
                    models.JSONField(
                        default=dict,
                        validators=[
                            plana.libs.validators.JsonSchemaValidator(
                                '/home/cspiga/Bureau/plana/back/plana/apps/contents/models/schemas/setting.json'
                            )
                        ],
                        verbose_name='Setting configuration',
                    ),
                ),
            ],
            options={
                'verbose_name': 'General setting',
                'verbose_name_plural': 'General settings',
                'ordering': ['setting'],
            },
        ),
    ]
