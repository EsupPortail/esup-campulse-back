# Generated by Django 3.2.16 on 2022-11-02 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('associations', '0004_auto_20221027_1621'),
    ]

    operations = [
        migrations.AlterField(
            model_name='association',
            name='is_enabled',
            field=models.BooleanField(default=False, verbose_name='Is enabled'),
        ),
    ]
