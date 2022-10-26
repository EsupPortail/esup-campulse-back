# Generated by Django 3.2.16 on 2022-10-26 08:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_activity_field', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Association',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username_association', models.CharField(default='', max_length=250, unique=True)),
                ('name_association', models.CharField(default='', max_length=250)),
                ('acronym_association', models.CharField(default='', max_length=30)),
                ('path_logo_association', models.CharField(default='', max_length=250)),
                ('description_association', models.TextField(default='')),
                ('activities_association', models.TextField(default='')),
                ('address_association', models.TextField(default='')),
                ('phone_association', models.CharField(default='', max_length=25)),
                ('email_association', models.CharField(default='', max_length=256)),
                ('siret_association', models.IntegerField(default=0)),
                ('website_association', models.CharField(default='', max_length=200)),
                ('student_amount_association', models.IntegerField(default=0)),
                ('is_enabled_association', models.BooleanField(default=False)),
                ('is_site_association', models.BooleanField(default=False)),
                ('created_date_association', models.DateTimeField(auto_now_add=True)),
                ('approval_date_association', models.DateTimeField(null=True)),
                ('last_goa_date_association', models.DateTimeField(null=True)),
                ('cga_date_association', models.DateTimeField(null=True)),
                ('activity_field', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='associations.activityfield')),
            ],
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_institution', models.CharField(max_length=250)),
                ('acronym_institution', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='InstitutionComponent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name_institution_component', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='SocialNetwork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_social_network', models.CharField(max_length=32)),
                ('location_social_network', models.CharField(max_length=200)),
                ('association', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='associations.association')),
            ],
        ),
        migrations.AddField(
            model_name='association',
            name='institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='associations.institution'),
        ),
        migrations.AddField(
            model_name='association',
            name='institution_component',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='associations.institutioncomponent'),
        ),
    ]