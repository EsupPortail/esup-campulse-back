"""
Storage management from octant.

https://git.unistra.fr/di/cesar/octant/back/-/blob/develop/octant/apps/api/storages.py
"""
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.fields.files import FieldFile
from pyrage import decrypt, encrypt, x25519
from storages.backends.s3boto3 import S3Boto3Storage
from storages.utils import clean_name
from thumbnails.fields import ImageField as ThumbnailImageField
from thumbnails.files import ThumbnailedImageFile, ThumbnailManager

PUBLIC_ACL = "public-read"
PRIVATE_ACL = "private"

PUBLIC_CLASSES_NAMES = ["Association", "Document"]
PRIVATE_CLASSES_NAMES = ["DocumentUpload"]


class MediaStorage(S3Boto3Storage):
    """Default storage."""

    location = "media"

    def url(self, name, parameters=None, expire=None, http_method=None):
        super().url(name, parameters, expire, http_method)


class UpdateACLStorage(S3Boto3Storage):
    """Inspired by https://medium.com/@hiteshgarg14/how-to-dynamically-select-storage-in-django-filefield-bc2e8f5883fd"""

    def update_acl(self, name, acl=None):
        acl = acl or self.default_acl
        name = self._normalize_name(clean_name(name))
        self.bucket.Object(name).Acl().put(ACL=acl)


class PublicFileStorage(UpdateACLStorage):
    """Storage used for public files."""

    default_acl = PUBLIC_ACL
    file_overwrite = False
    querystring_auth = False


class PrivateFileStorage(UpdateACLStorage):
    """Storage used for private files."""

    default_acl = PRIVATE_ACL
    file_overwrite = False
    custom_domain = False
    querystring_auth = True


class EncryptedPrivateFileStorage(PrivateFileStorage):
    """Storage used for encrypted files."""

    def __init__(self):
        super().__init__()
        self.age_public_key = settings.AGE_PUBLIC_KEY
        self.age_private_key = settings.AGE_PRIVATE_KEY

        try:
            self.identity = x25519.Identity.from_str(
                self.age_private_key.decode("utf-8").strip()
            )
        except Exception as error:
            raise ImproperlyConfigured(f"AGE private key not found : {error}")

        try:
            self.recipient = x25519.Recipient.from_str(
                self.age_public_key.decode("utf-8").strip()
            )
        except Exception as error:
            raise ImproperlyConfigured(f"AGE public key not found : {error}")

    def _open(self, name, mode="rb"):
        file = super()._open(name, mode)
        decrypted_file = self._decrypt(file)
        return decrypted_file

    def _save(self, name, content):
        encrypted_file = self._encrypt(content)
        return super()._save(name, encrypted_file)

    def _encrypt(self, original_file):
        file_content = original_file.file.read()
        encryption_result = encrypt(file_content, [self.recipient])
        encrypted_file = InMemoryUploadedFile(
            BytesIO(encryption_result),
            # TODO Find a better way to handle field_name for large files.
            original_file.field_name if hasattr(original_file, "field_name") else None,
            original_file.name,
            original_file.content_type,
            len(encryption_result),
            original_file.charset,
            original_file.content_type_extra,
        )
        return encrypted_file

    def _decrypt(self, original_file):
        file = original_file.read()
        decryption_result = decrypt(file, [self.identity])
        original_file.file._file = BytesIO(decryption_result)
        return original_file


class DynamicStorageFieldFile(FieldFile):
    """Override default Django FieldFile."""

    def __init__(self, instance, field, name):
        super().__init__(instance, field, name)
        self.storage = PublicFileStorage()
        if instance.__class__.__name__ in PRIVATE_CLASSES_NAMES:
            self.storage = EncryptedPrivateFileStorage()
        else:
            self.storage = PublicFileStorage()

    def update_acl(self):
        if not self:
            return
        # Only close the file if it's already open, which we know by
        # the presence of self._file
        if hasattr(self, "_file"):
            self.close()  # This update_acl method we have already defined in UpdateACLStorage
        self.storage.update_acl(self.name)


class DynamicStorageThumbnailedFieldFile(ThumbnailedImageFile):
    """FieldFile used with django-thumbnails."""

    querystring_expire = 60 * 60 * 24

    def __init__(self, instance, field, name, **kwargs):
        FieldFile.__init__(self, instance, field, name)
        if instance.__class__.__name__ in PRIVATE_CLASSES_NAMES:
            self.storage = EncryptedPrivateFileStorage(
                querystring_expire=self.querystring_expire
            )
        else:
            self.storage = PublicFileStorage()

        self.metadata_backend = field.metadata_backend
        self.thumbnails = ThumbnailManager(
            metadata_backend=self.metadata_backend,
            storage=self.storage,
            source_image=self,
        )

    def update_acl(self):
        if not self:
            return
        if hasattr(self, "_file"):
            self.close()
        self.storage.update_acl(self.name)

    def delete(self, with_thumbnails=True, save=True, *args, **kwargs):
        """Delete thumbnails and original file."""
        if not with_thumbnails:
            super().delete(save=save)
            return

        self.thumbnails.delete_all()
        super().delete(save=save)


class DynamicStorageFileField(models.FileField):
    """Override default Django FileField."""

    attr_class = DynamicStorageFieldFile

    def pre_save(self, model_instance, add):
        if model_instance.__class__.__name__ in PRIVATE_CLASSES_NAMES:
            storage = EncryptedPrivateFileStorage()
        else:
            storage = PublicFileStorage()

        file = super().pre_save(model_instance, add)
        file.storage = storage

        if file and file._committed:
            # This update_acl method we have already defined
            # in DynamicStorageFieldFile class above.
            file.update_acl()

        return file


class DynamicThumbnailImageField(ThumbnailImageField):
    """ImageField used with django-thumbnails."""

    attr_class = DynamicStorageThumbnailedFieldFile

    def pre_save(self, model_instance, add):
        if model_instance.__class__.__name__ in PRIVATE_CLASSES_NAMES:
            storage = EncryptedPrivateFileStorage()
        else:
            storage = PublicFileStorage()

        file = super().pre_save(model_instance, add)
        file.storage = storage

        if file and file._committed:
            file.update_acl()

        return file
