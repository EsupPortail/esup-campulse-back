"""Unittests for projects custom permissions."""
from unittest.mock import Mock
from django.test import TestCase

from plana.apps.projects.permissions import CanAccessOrEditProjectPermission


class CanAccessOrEditProjectPermissionTestCase(TestCase):

    def setUp(self):
        self.permission = CanAccessOrEditProjectPermission()
        self.request = Mock()
        self.request.user = Mock()
        self.view = Mock()

    def test_can_access_or_edit_project_permission_has_permission(self):
        self.request.user.is_authenticated = True
        self.assertTrue(self.permission.has_permission(self.request, self.view))

        self.request.user.is_authenticated = False
        self.assertFalse(self.permission.has_permission(self.request, self.view))

        self.request.user = None
        self.assertFalse(self.permission.has_permission(self.request, self.view))

    def test_can_access_or_edit_project_permission_has_object_permission_safe_methods(self):
        safe_methods = ('GET', 'HEAD', 'OPTIONS')
        project = Mock(spec=[])

        for method in safe_methods:
            self.request.user.reset_mock()

            self.request.user.can_access_project.return_value = True
            self.request.method = method
            has_perm = self.permission.has_object_permission(self.request, self.view, project)

            self.assertTrue(has_perm)
            self.request.user.can_access_project.assert_called_once_with(project)
            self.request.user.can_edit_project.assert_not_called()

    def test_can_access_or_edit_project_permission_has_object_permission_unsafe_methods(self):
        unsafe_methods = ('POST', 'PUT', 'PATCH', 'DELETE')
        project = Mock(spec=[])

        for method in unsafe_methods:
            self.request.user.reset_mock()

            self.request.user.can_edit_project.return_value = True
            self.request.method = method
            has_perm = self.permission.has_object_permission(self.request, self.view, project)

            self.assertTrue(has_perm)
            self.request.user.can_edit_project.assert_called_with(project)
            self.request.user.can_access_project.assert_not_called()

    def test_can_access_or_edit_project_permission_has_object_permission_linked_object(self):
        # Simulating an object linked to a project here
        parent_project = Mock()
        linked_obj = Mock(project=parent_project)

        self.request.method = 'GET'
        self.request.user.can_access_project.return_value = True
        has_perm = self.permission.has_object_permission(self.request, self.view, linked_obj)
        self.assertTrue(has_perm)
        self.request.user.can_access_project.assert_called_once_with(parent_project)
