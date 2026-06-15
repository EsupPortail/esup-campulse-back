"""Custom permissions for projects app"""

from rest_framework import permissions
from plana.apps.projects.models import Project


class ProjectCommentUpdateDestroyPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        """Only the author of the comment can update it, and only if the project is not closed"""
        if not request.user.is_superuser and obj.user != request.user:
            return False

        if obj.project.project_status not in Project.ProjectStatus.get_commentable_project_statuses():
            return False

        return True


class ProjectUpdatePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user.can_edit_project(project_obj=obj)
