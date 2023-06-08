from django.contrib.postgres.operations import UnaccentExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('associations', '0014_alter_association_path_logo'),
    ]

    operations = [UnaccentExtension()]
