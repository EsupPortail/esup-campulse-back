# Generated by Django 3.2.20 on 2023-08-23 08:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0025_documentupload_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documentupload',
            name='comment',
            field=models.TextField(null=True, verbose_name='Comment'),
        ),
    ]
