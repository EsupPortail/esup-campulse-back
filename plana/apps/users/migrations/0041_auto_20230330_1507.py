# Generated by Django 3.2.16 on 2023-03-30 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('associations', '0032_auto_20230322_0825'),
        ('institutions', '0003_remove_institution_email'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('commissions', '0001_initial'),
        ('users', '0040_alter_user_options'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AssociationUsers',
            new_name='AssociationUser',
        ),
        migrations.RenameModel(
            old_name='GroupInstitutionCommissionUsers',
            new_name='GroupInstitutionCommissionUser',
        ),
        migrations.AlterModelOptions(
            name='associationuser',
            options={
                'permissions': [
                    (
                        'change_associationuser_any_institution',
                        'Can change associations for all users.',
                    ),
                    (
                        'delete_associationuser_any_institution',
                        'Can delete associations for all users.',
                    ),
                    (
                        'view_associationuser_anyone',
                        'Can view all associations for a user.',
                    ),
                ],
                'verbose_name': 'Association',
                'verbose_name_plural': 'Associations',
            },
        ),
        migrations.AlterModelOptions(
            name='groupinstitutioncommissionuser',
            options={
                'permissions': [
                    (
                        'add_groupinstitutioncommissionuser_any_group',
                        'Can add restricted groups to a user.',
                    ),
                    (
                        'delete_groupinstitutioncommissionuser_any_group',
                        'Can delete restricted groups to a user.',
                    ),
                    (
                        'view_groupinstitutioncommissionuser_any_group',
                        'Can view all groups for a user.',
                    ),
                ],
                'verbose_name': 'User Institution Commission Groups',
                'verbose_name_plural': 'Users Institution Commission Groups',
            },
        ),
        migrations.RemoveField(
            model_name='user',
            name='groups_institutions',
        ),
        migrations.AddField(
            model_name='user',
            name='groups_institutions_commissions',
            field=models.ManyToManyField(
                related_name='group_institution_commission_set',
                through='users.GroupInstitutionCommissionUser',
                to='auth.Group',
                verbose_name='Groups',
            ),
        ),
    ]