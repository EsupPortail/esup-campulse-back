# Generated by Django 3.2.16 on 2022-11-14 13:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("associations", "0005_alter_association_is_enabled"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="activityfield",
            options={
                "verbose_name": "Domaine d'activité",
                "verbose_name_plural": "Domaines d'activités",
            },
        ),
        migrations.AlterModelOptions(
            name="institution",
            options={
                "verbose_name": "Etablissement",
                "verbose_name_plural": "Etablissements",
            },
        ),
        migrations.AlterModelOptions(
            name="institutioncomponent",
            options={
                "verbose_name": "Composante",
                "verbose_name_plural": "Composantes",
            },
        ),
        migrations.AlterModelOptions(
            name="socialnetwork",
            options={
                "verbose_name": "Réseau social",
                "verbose_name_plural": "Réseaux sociaux",
            },
        ),
        migrations.AlterField(
            model_name="association",
            name="acronym",
            field=models.CharField(default="", max_length=30, verbose_name="Acronyme"),
        ),
        migrations.AlterField(
            model_name="association",
            name="activities",
            field=models.TextField(default="", verbose_name="Activités"),
        ),
        migrations.AlterField(
            model_name="association",
            name="activity_field",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                to="associations.activityfield",
                verbose_name="Domaine d'activité",
            ),
        ),
        migrations.AlterField(
            model_name="association",
            name="address",
            field=models.TextField(default="", verbose_name="Adresse"),
        ),
        migrations.AlterField(
            model_name="association",
            name="approval_date",
            field=models.DateTimeField(null=True, verbose_name="Date d'agrément"),
        ),
        migrations.AlterField(
            model_name="association",
            name="cga_date",
            field=models.DateTimeField(
                null=True, verbose_name="Date de dernière AG constitutive"
            ),
        ),
        migrations.AlterField(
            model_name="association",
            name="creation_date",
            field=models.DateTimeField(
                auto_now_add=True, verbose_name="Date de création"
            ),
        ),
        migrations.AlterField(
            model_name="association",
            name="institution",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="associations",
                to="associations.institution",
                verbose_name="Etablissement",
            ),
        ),
        migrations.AlterField(
            model_name="association",
            name="institution_component",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.RESTRICT,
                related_name="associations",
                to="associations.institutioncomponent",
                verbose_name="Composante",
            ),
        ),
        migrations.AlterField(
            model_name="association",
            name="is_site",
            field=models.BooleanField(default=False, verbose_name="Site ?"),
        ),
        migrations.AlterField(
            model_name="association",
            name="last_goa_date",
            field=models.DateTimeField(
                null=True, verbose_name="Date de la dernière AGO"
            ),
        ),
        migrations.AlterField(
            model_name="association",
            name="path_logo",
            field=models.CharField(
                default="", max_length=250, verbose_name="Emplacement du logo"
            ),
        ),
        migrations.AlterField(
            model_name="association",
            name="phone",
            field=models.CharField(default="", max_length=25, verbose_name="Téléphone"),
        ),
        migrations.AlterField(
            model_name="association",
            name="student_count",
            field=models.IntegerField(default=0, verbose_name="Nombre d'étudiants"),
        ),
        migrations.AlterField(
            model_name="association",
            name="website",
            field=models.URLField(default="", verbose_name="Site"),
        ),
        migrations.AlterField(
            model_name="institution",
            name="acronym",
            field=models.CharField(max_length=30, verbose_name="Acronyme"),
        ),
        migrations.AlterField(
            model_name="socialnetwork",
            name="location",
            field=models.URLField(verbose_name="Adresse"),
        ),
    ]