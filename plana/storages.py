"""
Storage management from octant.

https://git.unistra.fr/di/cesar/octant/back/-/blob/develop/octant/apps/api/storages.py
"""
from django.db import models
from django.db.models.fields.files import FieldFile
from storages.backends.s3boto3 import S3Boto3Storage
from storages.utils import clean_name
from thumbnails.fields import ImageField as ThumbnailImageField
from thumbnails.files import ThumbnailedImageFile, ThumbnailManager
from thumbnails.models import Source

PUBLIC_ACL = "public-read"
PRIVATE_ACL = "private"

PUBLIC_CLASSES_NAMES = ["Association", "Document"]
PRIVATE_CLASSES_NAMES = ["DocumentUpload"]


class MediaStorage(S3Boto3Storage):
    location = "media"

    def url(self, name, parameters=None, expire=None, http_method=None):
        super().url(name, parameters, expire, http_method)


class UpdateACLStorage(S3Boto3Storage):
    # Inspired by https://medium.com/@hiteshgarg14/how-to-dynamically-select-storage-in-django-filefield-bc2e8f5883fd

    def update_acl(self, name, acl=None):
        acl = acl or self.default_acl
        name = self._normalize_name(clean_name(name))
        self.bucket.Object(name).Acl().put(ACL=acl)


class PublicFileStorage(UpdateACLStorage):
    default_acl = PUBLIC_ACL
    file_overwrite = False
    querystring_auth = False


class PrivateFileStorage(UpdateACLStorage):
    default_acl = PRIVATE_ACL
    file_overwrite = False
    custom_domain = False
    querystring_auth = True


class DynamicStorageFieldFile(FieldFile):
    def __init__(self, instance, field, name):
        super().__init__(instance, field, name)
        self.storage = PublicFileStorage()
        if instance.__class__.__name__ in PRIVATE_CLASSES_NAMES:
            self.storage = PrivateFileStorage()
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


class DynamicStorageFileField(models.FileField):
    attr_class = DynamicStorageFieldFile

    def pre_save(self, model_instance, add):
        storage = PublicFileStorage()
        if model_instance.__class__.__name__ in PRIVATE_CLASSES_NAMES:
            storage = PrivateFileStorage()
        else:
            storage = PublicFileStorage()

        file = super().pre_save(model_instance, add)
        file.storage = storage

        if file and file._committed:
            # This update_acl method we have already defined
            # in DynamicStorageFieldFile class above.
            file.update_acl()
        return file


class DynamicStorageThumbnailedFieldFile(ThumbnailedImageFile):
    """FieldFile used with django-thumbnails."""

    querystring_expire = 60 * 60 * 24

    def __init__(self, instance, field, name, **kwargs):
        FieldFile.__init__(self, instance, field, name)
        if instance.__class__.__name__ in PRIVATE_CLASSES_NAMES:
            self.storage = PrivateFileStorage(
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
        if not with_thumbnails:
            super().delete(save=save)
            return

        self.thumbnails.delete_all()
        super().delete(save=save)


class DynamicThumbnailImageField(ThumbnailImageField):
    """ImageField used with django-thumbnails."""

    attr_class = DynamicStorageThumbnailedFieldFile

    def pre_save(self, model_instance, add):
        if model_instance.__class__.__name__ in PRIVATE_CLASSES_NAMES:
            storage = PrivateFileStorage()
        else:
            storage = PublicFileStorage()

        file = super().pre_save(model_instance, add)
        file.storage = storage

        if file and file._committed:
            file.update_acl()

        return file
