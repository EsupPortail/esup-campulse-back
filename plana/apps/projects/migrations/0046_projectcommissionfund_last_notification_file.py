# Generated by Django 4.2.16 on 2025-03-04 09:44

import django.core.validators
from django.db import migrations
import plana.storages


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0045_alter_project_association_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectcommissionfund',
            name='last_notification_file',
            field=plana.storages.DynamicStorageFileField(
                blank=True,
                upload_to='',
                validators=[django.core.validators.FileExtensionValidator(['pdf'])],
                verbose_name='Last notification file',
            ),
        ),
    ]
