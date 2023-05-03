"""Views directly linked to projects comments."""
from rest_framework import generics, response, status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.projects.serializers.project_comment import (ProjectCommentSerializer, ProjectCommentDataSerializer)


class ProjectCommentCreate(generics.ListCreateAPIView):
    """/projects/comments route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectComment.objects.all()
    serializer_class = ProjectCommentSerializer