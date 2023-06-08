"""Views directly linked to document uploads."""
from pathlib import Path

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import FileResponse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.documents.serializers.document_upload import (
    DocumentUploadCreateSerializer,
    DocumentUploadFileSerializer,
    DocumentUploadSerializer,
)
from plana.apps.projects.models.project import Project
from plana.apps.users.models.user import AssociationUser


class DocumentUploadListCreate(generics.ListCreateAPIView):
    """/documents/uploads route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = DocumentUpload.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            self.serializer_class = DocumentUploadCreateSerializer
        else:
            self.serializer_class = DocumentUploadSerializer
        return super().get_serializer_class()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "user_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by User ID.",
            ),
            OpenApiParameter(
                "association_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by Association ID.",
            ),
            OpenApiParameter(
                "project_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by Project ID.",
            ),
            OpenApiParameter(
                "process_types",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Document process type.",
            ),
        ],
        responses={
            status.HTTP_200_OK: DocumentUploadSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
        },
        tags=["documents/uploads"],
    )
    def get(self, request, *args, **kwargs):
        """Lists all documents uploads."""
        user = request.query_params.get("user_id")
        association = request.query_params.get("association_id")
        project = request.query_params.get("project_id")
        process_types = request.query_params.get("process_types")

        if not request.user.has_perm("documents.view_documentupload_all"):
            user_associations_ids = AssociationUser.objects.filter(
                user_id=request.user.pk
            ).values_list("association_id")
            user_documents_ids = DocumentUpload.objects.filter(
                models.Q(user_id=request.user.pk)
                | models.Q(association_id__in=user_associations_ids)
            ).values_list("id")
            self.queryset = self.queryset.filter(id__in=user_documents_ids)

        if user is not None and user != "":
            self.queryset = self.queryset.filter(user_id=user)

        if association is not None and association != "":
            self.queryset = self.queryset.filter(association_id=association)

        if project is not None and project != "":
            self.queryset = self.queryset.filter(project_id=project)

        if process_types is not None and process_types != "":
            all_process_types = [c[0] for c in Document.process_type.field.choices]
            process_types_codes = process_types.split(",")
            process_types_codes = [
                project_type_code
                for project_type_code in process_types_codes
                if project_type_code != "" and project_type_code in all_process_types
            ]
            self.queryset = self.queryset.filter(
                document_id__in=Document.objects.filter(
                    process_type__in=process_types_codes
                ).values_list("id")
            )

        return self.list(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: DocumentUploadCreateSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: None,
        },
        tags=["documents/uploads"],
    )
    def post(self, request, *args, **kwargs):
        """Creates a new document upload."""
        if "document" not in request.data:
            return response.Response(
                {"error": _("Document does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            document = Document.objects.get(id=request.data["document"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Document does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )
        existing_document = DocumentUpload.objects.filter(document_id=document.id)

        if "project" in request.data:
            try:
                project = Project.visible_objects.get(id=request.data["project"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("Project does not exist.")},
                    status=status.HTTP_404_NOT_FOUND,
                )
            existing_document = existing_document.filter(project_id=project.id)
            if not request.user.can_access_project(project):
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
                association = Association.objects.get(id=request.data["association"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("Association does not exist.")},
                    status=status.HTTP_404_NOT_FOUND,
                )
            existing_document = existing_document.filter(association_id=association.id)
            if not request.user.has_perm(
                "documents.add_documentupload_all"
            ) and not request.user.is_president_in_association(
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
        ):
            existing_document = existing_document.filter(user_id=request.user.pk)
            if (
                not request.user.has_perm("documents.add_documentupload_all")
                and int(request.data["user"]) != request.user.pk
            ):
                return response.Response(
                    {"error": _("Not allowed to upload documents with this user.")},
                    status=status.HTTP_403_FORBIDDEN,
                )

        # TODO Re-enable serializer when fixtures for unit tests will be OK.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        """

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

        if not document.is_multiple and existing_document.count() > 0:
            return response.Response(
                {"error": _("Document cannot be submitted multiple times.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.data["path_file"].content_type not in document.mime_types:
            return response.Response(
                {"error": _("Wrong media type for this document.")},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        # request.data["name"] = f"{slugify(document.name)}{'.'.join(Path(request.data["path_file"].name).suffixes)}"
        request.data["name"] = request.data["path_file"].name

        return super().create(request, *args, **kwargs)


class DocumentUploadRetrieveDestroy(generics.RetrieveDestroyAPIView):
    """/documents/uploads/{id} route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentUploadSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: DocumentUploadSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["documents/uploads"],
    )
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
                and not request.user.can_access_project(
                    Project.visible_objects.get(id=document_upload.project_id)
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

        serializer = self.serializer_class(self.queryset.get(id=kwargs["pk"]))
        return response.Response(serializer.data)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: DocumentUploadSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["documents/uploads"],
    )
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
                and not request.user.can_access_project(
                    Project.visible_objects.get(id=document_upload.project_id)
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
                {"error": _("Not allowed to delete this uploaded document.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        return self.destroy(request, *args, **kwargs)


class DocumentUploadFileRetrieve(generics.RetrieveAPIView):
    """/documents/uploads/{id}/file route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = DocumentUpload.objects.all()
    serializer_class = DocumentUploadFileSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: DocumentUploadFileSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["documents/uploads"],
    )
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
                and not request.user.can_access_project(
                    Project.visible_objects.get(id=document_upload.project_id)
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

        file = document_upload.path_file.open(mode="r+b")
        return FileResponse(
            file.open(),
            as_attachment=False,
            filename=document_upload.name,
        )
