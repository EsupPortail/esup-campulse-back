# Generated by Django 3.2.16 on 2023-07-07 07:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contents', '0005_rename_sidebar_content_aside'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='title',
            field=models.CharField(default='', max_length=512, verbose_name='Title'),
        ),
    ]
