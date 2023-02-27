"""
Storage tests from octant.

https://git.unistra.fr/di/cesar/octant/back/-/blob/develop/octant/apps/api/tests/test_storages.py
"""
from unittest.mock import Mock

from django.core.files.storage import default_storage
from django.test import TestCase

from plana.apps.associations.storages import (
    DynamicStorageFieldFile,
    PrivateFileStorage,
    PublicFileStorage,
)


class UpdateACLStorageTest(TestCase):
    def test_public_update_acl_method(self):
        public_storage = PublicFileStorage()
        bucket = Mock()
        put = bucket.Object.return_value.Acl.return_value.put
        public_storage._bucket = bucket
        public_storage.update_acl("name")
        put.assert_called_with(ACL=PublicFileStorage.default_acl)
        self.assertEqual(put.call_count, 1)

    def test_private_update_acl_method(self):
        private_storage = PrivateFileStorage()
        bucket = Mock()
        put = bucket.Object.return_value.Acl.return_value.put
        private_storage._bucket = bucket
        private_storage.update_acl("name")
        put.assert_called_with(ACL=PrivateFileStorage.default_acl)
        self.assertEqual(put.call_count, 1)


class DynamicStorageFieldFileTest(TestCase):
    def test_file_field_is_initialized_with_correct_storage_class(self):
        field = Mock()
        field.storage = default_storage

        public_instance = Mock()
        public_instance.is_public = True
        file = DynamicStorageFieldFile(public_instance, field=field, name="Name")
        self.assertIsInstance(file.storage, PublicFileStorage)

        private_instance = Mock()
        private_instance.is_public = False
        file = DynamicStorageFieldFile(private_instance, field=field, name="Name")
        self.assertIsInstance(file.storage, PrivateFileStorage)

    def test_file_field_update_acl_method_calls_update_acl_from_storage(self):
        field = Mock()
        field.storage = default_storage
        public_instance = Mock()
        public_instance.is_public = True
        file = DynamicStorageFieldFile(
            public_instance, field=field, name="filename.ext"
        )
        file.storage = Mock()
        file.update_acl()
        file.storage.update_acl.assert_called_once_with("filename.ext")
