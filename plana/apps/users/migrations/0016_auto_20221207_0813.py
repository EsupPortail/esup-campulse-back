# Generated by Django 3.2.16 on 2022-12-07 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0015_auto_20221125_1527"),
    ]

    operations = [
        migrations.AddField(
            model_name="associationusers",
            name="is_president",
            field=models.BooleanField(default=False, verbose_name="Is president"),
        ),
        migrations.AddField(
            model_name="associationusers",
            name="role_name",
            field=models.CharField(
                default="", max_length=150, null=True, verbose_name="Role name"
            ),
        ),
    ]
