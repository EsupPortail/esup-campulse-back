# Generated by Django 3.2.19 on 2023-06-02 07:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('commissions', '0004_rename_commissiondate_commission'),
        ('projects', '0021_alter_projectcomment_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectcommissiondate',
            name='commission_date',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='commissions.commission',
                verbose_name='Commission',
            ),
        ),
    ]
