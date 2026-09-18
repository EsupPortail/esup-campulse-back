"""Views directly linked to projects comments."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.projects import permissions
from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.projects.serializers.project_comment import (
    ProjectCommentDataSerializer,
    ProjectCommentSerializer,
    ProjectCommentUpdateSerializer,
)


@extend_schema_view(
    get=extend_schema(tags=["projects/comments"]),
    post=extend_schema(tags=["projects/comments"]),
)
class ProjectCommentListCreate(generics.ListCreateAPIView):
    """/projects/{project_id}/comments route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions, permissions.ProjectCommentListPermission]
    queryset = ProjectComment.objects.all()
    serializer_class = ProjectCommentSerializer

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProjectCommentDataSerializer
        return ProjectCommentSerializer

    def get_queryset(self):
        if not self.request.user.has_perm("projects.view_projectcomment_not_visible"):
            return self.queryset.filter(project_id=self.kwargs.get("project_id"), is_visible=True)
        return self.queryset.filter(project_id=self.kwargs.get("project_id"))


@extend_schema_view(
    patch=extend_schema(tags=["projects/comments"]),
    delete=extend_schema(tags=["projects/comments"]),
)
class ProjectCommentUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/projects/{project_id}/comments/{pk} route."""

    queryset = ProjectComment.objects.all()
    serializer_class = ProjectCommentUpdateSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions, permissions.ProjectCommentUpdateDestroyPermission]
    http_method_names = ["patch", "delete"]

    def get_queryset(self):
        return ProjectComment.objects.filter(project_id=self.kwargs["project_id"])
