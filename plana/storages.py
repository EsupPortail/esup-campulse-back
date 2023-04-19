"""
Storage management from octant.

https://git.unistra.fr/di/cesar/octant/back/-/blob/develop/octant/apps/api/storages.py
"""
from io import BytesIO

from django.core.exceptions import ImproperlyConfigured
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models.fields.files import FieldFile
from pyrage import decrypt, encrypt, ssh
from storages.backends.s3boto3 import S3Boto3Storage
from storages.utils import clean_name
from thumbnails.fields import ImageField as ThumbnailImageField
from thumbnails.files import ThumbnailedImageFile, ThumbnailManager

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


class EncryptedPrivateFileStorage(PrivateFileStorage):
    def __init__(self):
        super().__init__()

        try:
            id_rsa_pub_file = open("~/.ssh/id_ed25519.pub")
            public_content = id_rsa_pub_file.read()
            self.recipient = ssh.Recipient.from_str(public_content)
            id_rsa_pub_file.close()
        except Exception as e:
            raise ImproperlyConfigured(f"Public key not found : {e}")

        try:
            id_rsa_file = open("~/.ssh/id_ed25519")
            private_content = id_rsa_file.read()
            self.identity = ssh.Identity.from_buffer(bytes(private_content, "utf-8"))
            print("IDENTITY")
            print(self.identity)
            id_rsa_file.close()
        except Exception as e:
            raise ImproperlyConfigured(f"Private key not found : {e}")

    def _open(self, name, mode='rb'):
        file = super()._open(name, mode)
        decrypted_file = self._decrypt(file)
        return decrypted_file

    def _save(self, path, file):
        encrypted_file = self._encrypt(file)
        return super()._save(path, encrypted_file)

    def _encrypt(self, original_file):
        encryption_result = encrypt(BytesIO(original_file), [self.recipient])
        print("ENCRYPTION RESULT")
        print(encryption_result)
        encrypted_file = InMemoryUploadedFile(
            BytesIO(encryption_result.data),
            original_file.field_name,
            original_file.name,
            original_file.content_type,
            len(encryption_result.data),
            original_file.charset,
            original_file.content_type_extra,
        )
        print("ENCRYPTED FILE")
        print(encrypted_file)
        return encrypted_file

    def _decrypt(self, original_file):
        decryption_result = decrypt(original_file, [self.identity])
        print("DECRYPTION RESULT")
        print(decryption_result)
        return decryption_result


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
