import os
import shutil

import boto3
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _


class Command(BaseCommand):
    help = _("Removes S3 bucket content.")

    def handle(self, *args, **options):
        try:
            if settings.USE_S3 == True:
                bucket_name = settings.AWS_STORAGE_PUBLIC_BUCKET_NAME
                resource = boto3.resource(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                )
                bucket = resource.Bucket(bucket_name)
                for s3_object in bucket.objects.all():
                    if not s3_object.key.startswith(settings.S3_PDF_FILEPATH):
                        s3_object.delete()

                self.stdout.write(self.style.SUCCESS(_(f"S3 bucket {bucket_name} content cleaned.")))
            else:
                shutil.rmtree(os.path.join(settings.MEDIA_ROOT))
                pass

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
