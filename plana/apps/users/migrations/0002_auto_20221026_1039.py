# Generated by Django 3.2.16 on 2022-10-26 08:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={"default_permissions": []},
        ),
        migrations.AddField(
            model_name="user",
            name="is_cas_user",
            field=models.BooleanField(default=False),
        ),
    ]
