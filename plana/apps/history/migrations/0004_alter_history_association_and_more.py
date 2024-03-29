# Generated by Django 4.2.6 on 2023-10-09 13:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0041_alter_projectcomment_options_and_more'),
        ('associations', '0043_alter_association_options'),
        ('users', '0054_user_is_student'),
        ('documents', '0027_document_edition_date'),
        ('history', '0003_remove_history_document_history_document_upload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='history',
            name='association',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='associations.association',
                verbose_name='Association affected by change',
            ),
        ),
        migrations.AlterField(
            model_name='history',
            name='association_user',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='users.associationuser',
                verbose_name='Link between association and user affected by change',
            ),
        ),
        migrations.AlterField(
            model_name='history',
            name='document_upload',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='documents.documentupload',
                verbose_name='Document affected by change',
            ),
        ),
        migrations.AlterField(
            model_name='history',
            name='group_institution_fund_user',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='users.groupinstitutionfunduser',
                verbose_name='Link between group and user affected by change',
            ),
        ),
        migrations.AlterField(
            model_name='history',
            name='project',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='projects.project',
                verbose_name='Project affected by change',
            ),
        ),
        migrations.AlterField(
            model_name='history',
            name='user',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='user_set',
                to=settings.AUTH_USER_MODEL,
                verbose_name='User affected by change',
            ),
        ),
    ]
