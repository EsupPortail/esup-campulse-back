# Generated by Django 3.2.16 on 2023-01-26 10:19

from django.db import migrations

import plana.apps.associations.models.association
import plana.storages


class Migration(migrations.Migration):
    dependencies = [
        ('associations', '0021_auto_20230126_1102'),
    ]

    operations = [
        migrations.AlterField(
            model_name='association',
            name='path_logo',
            field=plana.storages.DynamicThumbnailImageField(
                blank=True,
                null=True,
                upload_to=plana.apps.associations.models.association.get_logo_path,
                verbose_name='Dynamic thumbnails for the logo',
            ),
        ),
    ]
