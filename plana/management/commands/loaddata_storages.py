import datetime
import os
import pathlib
import shutil

import boto3
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from plana.apps.contents.models.logo import Logo
from plana.apps.documents.models.document import Document


class Command(BaseCommand):
    help = _("Loads S3 bucket initial content.")

    def handle(self, *args, **options):
        try:
            if settings.USE_S3 is True:
                bucket_name = settings.AWS_STORAGE_BUCKET_NAME
                resource = boto3.resource(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                )
                bucket = resource.Bucket(bucket_name)
                if sum(1 for _ in bucket.objects.all()) > 0:
                    self.stdout.write(self.style.WARNING(_("Initial storages data already present.")))
                else:
                    for file in pathlib.Path().glob("plana/apps/contents/fixtures/files/logos/*.*"):
                        with file.open(mode="rb") as logo_file:
                            bucket_object = bucket.put_object(
                                Key=f"{settings.S3_LOGOS_FILEPATH}/{datetime.datetime.now().year}/{file.name}",
                                Body=logo_file,
                            )
                            logo_object = Logo.objects.get(id=int(file.name.split("_")[0]))
                            logo_object.path_logo = bucket_object.key
                            logo_object.save()
                #    for file in pathlib.Path().glob("plana/apps/documents/fixtures/files/documents/*.*"):
                #        with file.open(mode="rb") as document_file:
                #            bucket_object = bucket.put_object(
                #                Key=f"{settings.S3_TEMPLATES_FILEPATH}/{datetime.datetime.now().year}/{file.name}",
                #                Body=document_file,
                #            )
                #            document_object = Document.objects.get(id=int(file.name.split("_")[0]))
                #            document_object.path_template = bucket_object.key
                #            document_object.save()

                    self.stdout.write(self.style.SUCCESS(_(f"S3 bucket {bucket_name} content loaded.")))
            else:
                shutil.rmtree(os.path.join(settings.MEDIA_ROOT))

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
