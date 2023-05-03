"""Views directly linked to projects comments."""
from rest_framework import generics, response, status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from drf_spectacular.utils import OpenApiParameter, extend_schema
from drf_spectacular.types import OpenApiTypes

from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.projects.serializers.project_comment import (ProjectCommentSerializer, ProjectCommentDataSerializer)


class ProjectCommentListCreate(generics.ListCreateAPIView):
    """/projects/comments route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectComment.objects.all()
    serializer_class = ProjectCommentSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "project_id",
                OpenApiTypes.NUMBER,
                OpenApiParameter.QUERY,
                description="Project id."
            ),
        ],
        responses={
            status.HTTP_200_OK: ProjectCommentSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        },
        tags=["projects/comments"]
    )
    def get(self, request, *args, **kwargs):
        """Lists all links between projects and comments"""
        project_id = request.query_params.get("project_id")

        if project_id:
            self.queryset = self.queryset.filter(project_id=project_id)
