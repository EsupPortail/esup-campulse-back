"""Views directly linked to document uploads."""
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, response, status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.documents.serializers.document_upload import DocumentUploadSerializer
from plana.apps.projects.models.project import Project
from plana.apps.users.models.user import AssociationUser


@extend_schema_view(
    get=extend_schema(tags=["documents/uploads"]),
    post=extend_schema(tags=["documents/uploads"]),
)
class DocumentUploadListCreate(generics.ListCreateAPIView):
    """/documents/uploads route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    serializer_class = DocumentUploadSerializer

    def get_queryset(self):
        queryset = DocumentUpload.objects.all()
        if self.request.method == "GET":
            if not self.request.user.has_perm("documents.view_documentupload_all"):
                user_associations_ids = AssociationUser.objects.filter(
                    user_id=self.request.user.pk
                ).values_list("association_id")
                user_documents_ids = DocumentUpload.objects.filter(
                    models.Q(user_id=self.request.user.pk)
                    | models.Q(association_id__in=user_associations_ids)
                ).values_list("id")
                queryset = queryset.filter(id__in=user_documents_ids)

        return queryset

    def get(self, request, *args, **kwargs):
        """Lists all documents uploads."""
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Creates a new document upload."""
        if "document" not in request.data:
            return response.Response(
                {"error": _("Document does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            document = Document.objects.get(pk=request.data["document"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Document does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if "project" in request.data:
            try:
                project = Project.objects.get(pk=request.data["project"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("Project does not exist.")},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if not request.user.can_edit_project(project):
                return response.Response(
                    {"error": _("Not allowed to upload documents for this project.")},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if (
            "association" in request.data
            and request.data["association"] is not None
            and request.data["association"] != ""
        ):
            try:
                Association.objects.get(pk=request.data["association"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("Association does not exist.")},
                    status=status.HTTP_404_NOT_FOUND,
                )
            if not request.user.is_president_in_association(
                request.data["association"]
            ):
                return response.Response(
                    {"error": _("Not allowed to post documents if not president.")},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if (
            "user" in request.data
            and request.data["user"] is not None
            and request.data["user"] != ""
            and (int(request.data["user"]) != request.user.pk)
        ):
            return response.Response(
                {"error": _("Not allowed to upload documents with this user.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "association" in request.data
            and request.data["association"] is not None
            and request.data["association"] != ""
        ) and (
            "user" in request.data
            and request.data["user"] is not None
            and request.data["user"] != ""
        ):
            return response.Response(
                {"error": _("A document upload can only have one affectation.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            not "association" in request.data
            or request.data["association"] is None
            or request.data["association"] == ""
        ) and (
            not "user" in request.data
            or request.data["user"] is None
            or request.data["user"] == ""
        ):
            return response.Response(
                {"error": _("Missing affectation of the new document upload.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.data["path_file"].content_type not in document.mime_types:
            return response.Response(
                {"error": _("Wrong media type for this document.")},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        return super().create(request, *args, **kwargs)


@extend_schema_view(
    get=extend_schema(tags=["documents/uploads"]),
    delete=extend_schema(tags=["documents/uploads"]),
)
class DocumentUploadRetrieveDestroy(generics.RetrieveDestroyAPIView):
    """/documents/uploads/{id} route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentUploadSerializer

    def get(self, request, *args, **kwargs):
        """Retrieves a document uploaded by a user."""
        try:
            document_upload = DocumentUpload.objects.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Document upload does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm("documents.view_documentupload_all") and (
            (
                document_upload.project_id is not None
                and not request.user.can_edit_project(
                    Project.objects.get(id=document_upload.project_id)
                )
            )
            or (
                document_upload.user_id is not None
                and request.user.pk != document_upload.user_id
            )
            or (
                document_upload.association_id is not None
                and not request.user.is_in_association(document_upload.association_id)
            )
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this uploaded document.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(self.queryset.filter(id=kwargs["pk"]))
        return response.Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        """Destroys an uploaded document."""
        try:
            document_upload = DocumentUpload.objects.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Document upload does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm("documents.delete_documentupload_all") and (
            (
                document_upload.project_id is not None
                and not request.user.can_edit_project(
                    Project.objects.get(id=document_upload.project_id)
                )
            )
            or (
                document_upload.user_id is not None
                and request.user.pk != document_upload.user_id
            )
            or (
                document_upload.association_id is not None
                and not request.user.is_in_association(document_upload.association_id)
            )
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this uploaded document.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        return self.destroy(request, *args, **kwargs)
