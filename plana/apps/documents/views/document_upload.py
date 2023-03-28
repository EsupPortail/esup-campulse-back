"""Views directly linked to document uploads."""

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.documents.serializers.document_upload import DocumentUploadSerializer
from plana.apps.projects.models.project import Project


class DocumentUploadListCreate(generics.ListCreateAPIView):
    """/documents/uploads route"""

    serializer_class = DocumentUploadSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_queryset(self):
        return DocumentUpload.objects.all()

    def get(self, request, *args, **kwargs):
        """Lists all documents uploads."""
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Creates a new document upload."""
        if "project" in request.data:
            try:
                project = Project.objects.get(pk=request.data["project"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("Project does not exist.")},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if not project.can_edit_project(request.user):
                return response.Response(
                    {"error": _("Not allowed to upload documents for this project.")},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return super().create(request, *args, **kwargs)
