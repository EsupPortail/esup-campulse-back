# Generated by Django 3.2.19 on 2023-06-01 07:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('documents', '0017_alter_document_commission'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='commission',
            new_name='fund',
        ),
    ]
