# Generated by Django 3.2.16 on 2022-12-13 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('consents', '0001_initial'),
        ('users', '0016_auto_20221207_0813'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='consents_given',
            field=models.ManyToManyField(
                through='users.GDPRConsentUsers',
                to='consents.GDPRConsent',
                verbose_name='GDPR Consents',
            ),
        ),
    ]
