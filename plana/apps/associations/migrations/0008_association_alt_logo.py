# Generated by Django 3.2.16 on 2022-12-02 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("associations", "0007_auto_20221125_1527"),
    ]

    operations = [
        migrations.AddField(
            model_name="association",
            name="alt_logo",
            field=models.TextField(default="", verbose_name="Description"),
        ),
    ]
