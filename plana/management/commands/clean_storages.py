import boto3
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _


class Command(BaseCommand):
    help = _("Resets S3 bucket content.")

    def handle(self, *args, **options):
        try:
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            resource = boto3.resource(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            )
            bucket = resource.Bucket(bucket_name)
            bucket.objects.all().delete()

            self.stdout.write(
                self.style.SUCCESS(_(f"S3 bucket {bucket_name} content cleaned."))
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR("Error : %s" % e))
