"""Custom permissions for projects app"""

from rest_framework import permissions
from rest_framework.generics import get_object_or_404

from plana.apps.projects.models import Project


class CanAccessOrEditProjectPermission(permissions.BasePermission):
    """
    Custom permission to check whether the request user can access or edit a project
    Works directly with a Project instance or any linked model with a 'project' attribute
    (ProjectCommissionFund, ProjectCategory, ...)
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        project = getattr(obj, "project", obj)

        # For GET, HEAD and OPTIONS
        if request.method in permissions.SAFE_METHODS:
            return request.user.can_access_project(project)

        # All other operations
        return request.user.can_edit_project(project)


class ProjectCommentUpdateDestroyPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        """Only the author of the comment can update it, and only if the project is not closed"""
        if not request.user.is_superuser and obj.user != request.user:
            return False

        if obj.project.project_status not in Project.ProjectStatus.get_commentable_project_statuses():
            return False

        return True


class ProjectCommentListPermission(permissions.BasePermission):
    """Custom permission to retrieve a project's comments"""

    def has_permission(self, request, view):
        project = get_object_or_404(Project.visible_objects.all(), pk=view.kwargs.get("project_id"))
        if (
            request.user.has_perm("projects.view_projectcomment_any_fund")
            or request.user.has_perm("projects.view_projectcomment_any_institution")
            or request.user.can_access_project(project)
        ):
            return True
        return False


class ProjectUpdatePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or request.user.can_edit_project(project_obj=obj)


class ProjectCategoryUpdatePermission(permissions.BasePermission):
    """
    Checks if user can edit project categories based on request data and if the user can edit the linked project or not
    """

    def has_permission(self, request, view):
        project_id = request.data.get("project")
        if not project_id:
            return True  # To let the serializer raise a payload error

        project = Project.objects.filter(pk=project_id).first()
        if not project:
            return True  # To let the serializer raise a "does not exist" error

        # If a project is given and does exist, returns if the user can edit it or not
        return request.user.can_edit_project(project)

    def has_object_permission(self, request, view, obj):
        return request.user.can_edit_project(obj.project)
