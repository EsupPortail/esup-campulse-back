# Generated by Django 3.2.19 on 2023-06-02 13:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('projects', '0023_rename_projectcommissiondate_projectcommissionfund'),
    ]

    operations = [
        migrations.RenameField(
            model_name='projectcommissionfund',
            old_name='commission_date',
            new_name='commission_fund',
        ),
    ]