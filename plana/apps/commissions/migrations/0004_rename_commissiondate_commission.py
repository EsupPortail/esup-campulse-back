# Generated by Django 3.2.19 on 2023-06-02 07:44

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0021_alter_projectcomment_options'),
        ('commissions', '0003_auto_20230531_0942'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CommissionDate',
            new_name='Commission',
        ),
    ]
