# Generated by Django 3.2.20 on 2023-08-25 10:09

from django.db import migrations, models

import plana.apps.contents.models.logo
import plana.storages


class Migration(migrations.Migration):
    dependencies = [
        ('contents', '0006_content_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='Logo',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('acronym', models.TextField(default='', verbose_name='Acronym')),
                ('title', models.TextField(default='', verbose_name='Logo alt')),
                ('url', models.TextField(default='', verbose_name='Site URL')),
                (
                    'path_logo',
                    plana.storages.DynamicStorageFileField(
                        blank=True,
                        null=True,
                        upload_to=plana.apps.contents.models.logo.get_logo_path,
                        verbose_name='Dynamic thumbnails for the logo',
                    ),
                ),
                (
                    'visible',
                    models.BooleanField(default=False, verbose_name='Is visible'),
                ),
            ],
            options={
                'verbose_name': 'Logo',
                'verbose_name_plural': 'Logos',
            },
        ),
    ]
