"""Custom tag to get a static file from a S3 server with private ACL."""

from django import template
from django.conf import settings

from plana.utils import get_s3_client

register = template.Library()


def s3static(object_key):
    """Call with {% s3static 'file/path' %}."""
    object_key = f"pdf/{object_key}"
    return get_s3_client().generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.AWS_STORAGE_PUBLIC_BUCKET_NAME,
            "Key": object_key,
        },
        ExpiresIn=3600,
    )
