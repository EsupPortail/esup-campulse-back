# Generated by Django 4.2.7 on 2023-11-17 13:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contents', '0008_logo_column_logo_row'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='aside',
            field=models.TextField(default='', null=True, verbose_name='Sidebar'),
        ),
        migrations.AlterField(
            model_name='content',
            name='footer',
            field=models.TextField(default='', null=True, verbose_name='Footer'),
        ),
        migrations.AlterField(
            model_name='content',
            name='header',
            field=models.TextField(default='', null=True, verbose_name='Header'),
        ),
        migrations.AlterField(
            model_name='content',
            name='title',
            field=models.CharField(default='', max_length=512, null=True, verbose_name='Title'),
        ),
    ]
