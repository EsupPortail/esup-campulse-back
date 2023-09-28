# Generated by Django 3.2.16 on 2022-11-24 14:54

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GDPRConsent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=256, verbose_name="GDPR Consent title"),
                ),
            ],
            options={
                "verbose_name": "GDPR Consent",
                "verbose_name_plural": "GDPR Consents",
            },
        ),
    ]
