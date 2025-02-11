"""Views directly linked to documents."""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.documents.models.document import Document
from plana.apps.documents.serializers.document import (
    DocumentCreateSerializer,
    DocumentSerializer,
    DocumentUpdateSerializer,
)

from plana.decorators import capture_queries


class DocumentList(generics.ListCreateAPIView):
    """/documents/ route."""

    queryset = Document.objects.all().order_by("name")

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "POST":
            self.serializer_class = DocumentCreateSerializer
        else:
            self.serializer_class = DocumentSerializer
        return super().get_serializer_class()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "acronym",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Document acronym.",
            ),
            OpenApiParameter(
                "fund_ids",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Document fund IDs.",
            ),
            OpenApiParameter(
                "process_types",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Document process type.",
            ),
        ],
        responses={
            status.HTTP_200_OK: DocumentSerializer,
        },
    )
    @capture_queries()
    def get(self, request, *args, **kwargs):
        """List all documents types."""
        acronym = request.query_params.get("acronym")
        fund_ids = request.query_params.get("fund_ids")
        process_types = request.query_params.get("process_types")

        if acronym is not None and acronym != "":
            self.queryset = self.queryset.filter(acronym=acronym)

        if fund_ids is not None and fund_ids != "":
            self.queryset = self.queryset.filter(fund_id__in=fund_ids.split(","))

        if process_types is not None and process_types != "":
            all_process_types = [c[0] for c in Document.process_type.field.choices]
            process_types_codes = process_types.split(",")
            process_types_codes = [
                project_type_code
                for project_type_code in process_types_codes
                if project_type_code != "" and project_type_code in all_process_types
            ]
            self.queryset = self.queryset.filter(process_type__in=process_types_codes)

        return self.list(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: DocumentSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        }
    )
    def post(self, request, *args, **kwargs):
        """Create a new document type (manager only)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if (
            "institution" in request.data
            and not request.user.has_perm("documents.add_document_any_institution")
            and not request.user.is_staff_in_institution(request.data["institution"])
        ):
            return response.Response(
                {"error": _("Not allowed to create a document for this institution.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "fund" in request.data
            and not request.user.has_perm("documents.add_document_any_fund")
            and not request.user.is_member_in_fund(request.data["fund"])
        ):
            return response.Response(
                {"error": _("Not allowed to create a document for this fund.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().create(request, *args, **kwargs)


class DocumentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/documents/{id} route."""

    queryset = Document.objects.all()
    http_method_names = ["get", "post", "patch", "delete", "head", "options", "trace"]

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            self.serializer_class = DocumentUpdateSerializer
        else:
            self.serializer_class = DocumentSerializer
        return super().get_serializer_class()

    @extend_schema(
        responses={
            status.HTTP_200_OK: DocumentSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: None,
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update document details."""

        document = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if (
            document.institution_id is not None
            and not request.user.has_perm("documents.change_document_any_institution")
            and not request.user.is_staff_in_institution(document.institution_id)
        ):
            return response.Response(
                {"error": _("Not allowed to update a document for this institution.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            document.fund_id is not None
            and not request.user.has_perm("documents.change_document_any_fund")
            and not request.user.is_member_in_fund(document.fund_id)
        ):
            return response.Response(
                {"error": _("Not allowed to update a document for this fund.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if document.process_type not in Document.ProcessType.get_updatable_documents():
            return response.Response(
                {"error": _("Not allowed to update a document with this process type.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            document.mime_types is not None
            and len(document.mime_types) != 0
            and request.data["path_template"].content_type not in document.mime_types
        ):
            return response.Response(
                {"error": _("Wrong media type for this document.")},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        return self.partial_update(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: DocumentSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def delete(self, request, *args, **kwargs):
        """Destroys an entire document type (manager only)."""
        document = self.get_object()

        if (
            document.institution_id is not None
            and not request.user.has_perm("documents.delete_document_any_institution")
            and not request.user.is_staff_in_institution(document.institution_id)
        ):
            return response.Response(
                {"error": _("Not allowed to delete a document for this institution.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            document.fund_id is not None
            and not request.user.has_perm("documents.delete_document_any_fund")
            and not request.user.is_member_in_fund(document.fund_id)
        ):
            return response.Response(
                {"error": _("Not allowed to delete a document for this fund.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if document.process_type != "NO_PROCESS":
            return response.Response(
                {"error": _("Not allowed to delete a document with a process type.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        return self.destroy(request, *args, **kwargs)
