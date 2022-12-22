# Generated by Django 3.2.16 on 2022-10-27 14:09

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("associations", "0002_auto_20221027_1407"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="activityfield",
            options={
                "verbose_name": "Activity field",
                "verbose_name_plural": "Activity fields",
            },
        ),
        migrations.AlterModelOptions(
            name="association",
            options={
                "verbose_name": "Association",
                "verbose_name_plural": "Associations",
            },
        ),
        migrations.AlterModelOptions(
            name="institution",
            options={
                "verbose_name": "Institution",
                "verbose_name_plural": "Institutions",
            },
        ),
        migrations.AlterModelOptions(
            name="institutioncomponent",
            options={
                "verbose_name": "Institution component",
                "verbose_name_plural": "Institution components",
            },
        ),
        migrations.AlterModelOptions(
            name="socialnetwork",
            options={
                "verbose_name": "Social network",
                "verbose_name_plural": "Social networks",
            },
        ),
        migrations.RemoveField(
            model_name="association",
            name="created_date",
        ),
        migrations.RemoveField(
            model_name="association",
            name="student_amount",
        ),
        migrations.RemoveField(
            model_name="association",
            name="username",
        ),
        migrations.AddField(
            model_name="association",
            name="creation_date",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Creation date",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="association",
            name="student_count",
            field=models.IntegerField(default=0, verbose_name="Student count"),
        ),
        migrations.AlterField(
            model_name="activityfield",
            name="name",
            field=models.CharField(max_length=250, verbose_name="Nom"),
        ),
        migrations.AlterField(
            model_name="association",
            name="acronym",
            field=models.CharField(default="", max_length=30, verbose_name="Acronym"),
        ),
        migrations.AlterField(
            model_name="association",
            name="activities",
            field=models.TextField(default="", verbose_name="Activities"),
        ),
        migrations.AlterField(
            model_name="association",
            name="activity_field",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                to="associations.activityfield",
                verbose_name="Activity field",
            ),
        ),
        migrations.AlterField(
            model_name="association",
            name="address",
            field=models.TextField(default="", verbose_name="Address"),
        ),
        migrations.AlterField(
            model_name="association",
            name="approval_date",
            field=models.DateTimeField(null=True, verbose_name="Approval date"),
        ),
        migrations.AlterField(
            model_name="association",
            name="cga_date",
            field=models.DateTimeField(null=True, verbose_name="CGA date"),
        ),
        migrations.AlterField(
            model_name="association",
            name="description",
            field=models.TextField(default="", verbose_name="Description"),
        ),
        migrations.AlterField(
            model_name="association",
            name="email",
            field=models.CharField(default="", max_length=256, verbose_name="Courriel"),
        ),
        migrations.AlterField(
            model_name="association",
            name="institution",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                to="associations.institution",
                verbose_name="Institution",
            ),
        ),
        migrations.AlterField(
            model_name="association",
            name="institution_component",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                to="associations.institutioncomponent",
                verbose_name="Institution component",
            ),
        ),
        migrations.AlterField(
            model_name="association",
            name="is_enabled",
            field=models.BooleanField(default=False, verbose_name="Is active"),
        ),
        migrations.AlterField(
            model_name="association",
            name="is_site",
            field=models.BooleanField(default=False, verbose_name="Is site"),
        ),
        migrations.AlterField(
            model_name="association",
            name="last_goa_date",
            field=models.DateTimeField(null=True, verbose_name="Last GOA date"),
        ),
        migrations.AlterField(
            model_name="association",
            name="name",
            field=models.CharField(
                default="", max_length=250, unique=True, verbose_name="Nom"
            ),
        ),
        migrations.AlterField(
            model_name="association",
            name="path_logo",
            field=models.CharField(
                default="", max_length=250, verbose_name="Logo path"
            ),
        ),
        migrations.AlterField(
            model_name="association",
            name="phone",
            field=models.CharField(default="", max_length=25, verbose_name="Phone"),
        ),
        migrations.AlterField(
            model_name="association",
            name="siret",
            field=models.IntegerField(default=0, verbose_name="SIRET"),
        ),
        migrations.AlterField(
            model_name="association",
            name="website",
            field=models.URLField(default="", verbose_name="Website"),
        ),
        migrations.AlterField(
            model_name="institution",
            name="acronym",
            field=models.CharField(max_length=30, verbose_name="Acronym"),
        ),
        migrations.AlterField(
            model_name="institution",
            name="name",
            field=models.CharField(max_length=250, verbose_name="Nom"),
        ),
        migrations.AlterField(
            model_name="institutioncomponent",
            name="name",
            field=models.CharField(max_length=250, verbose_name="Nom"),
        ),
        migrations.AlterField(
            model_name="socialnetwork",
            name="association",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="associations.association",
                verbose_name="Association",
            ),
        ),
        migrations.AlterField(
            model_name="socialnetwork",
            name="location",
            field=models.URLField(verbose_name="Emplacement"),
        ),
        migrations.AlterField(
            model_name="socialnetwork",
            name="type",
            field=models.CharField(max_length=32, verbose_name="Type"),
        ),
    ]
