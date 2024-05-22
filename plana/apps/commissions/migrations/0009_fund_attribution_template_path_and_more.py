# Generated by Django 4.2.11 on 2024-04-12 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('commissions', '0008_commission_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='fund',
            name='attribution_template_path',
            field=models.CharField(
                blank=True, default='', max_length=250, null=True, verbose_name='Attribution template path'
            ),
        ),
        migrations.AddField(
            model_name='fund',
            name='decision_attribution_template_path',
            field=models.CharField(
                blank=True, default='', max_length=250, null=True, verbose_name='Decision attribution template path'
            ),
        ),
        migrations.AddField(
            model_name='fund',
            name='postpone_template_path',
            field=models.CharField(
                blank=True, default='', max_length=250, null=True, verbose_name='Postpone template path'
            ),
        ),
        migrations.AddField(
            model_name='fund',
            name='rejection_template_path',
            field=models.CharField(
                blank=True, default='', max_length=250, null=True, verbose_name='Rejection template path'
            ),
        ),
    ]