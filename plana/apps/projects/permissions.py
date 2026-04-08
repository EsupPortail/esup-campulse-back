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
