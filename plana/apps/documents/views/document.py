"""Views directly linked to documents."""
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.documents.models.document import Document
from plana.apps.documents.serializers.document import DocumentSerializer


class DocumentList(generics.ListCreateAPIView):
    """/documents/ route"""

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "acronym",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Document acronym.",
            ),
            OpenApiParameter(
                "process_type",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Document process type.",
            ),
        ],
        responses={
            status.HTTP_200_OK: DocumentSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """Lists all documents types."""
        acronym = request.query_params.get("acronym")
        process_type = request.query_params.get("process_type")

        if acronym is not None and acronym != "":
            self.queryset = self.queryset.filter(acronym=acronym)

        if process_type is not None and process_type != "":
            self.queryset = self.queryset.filter(process_type=process_type)

        return self.list(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: DocumentSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        }
    )
    def post(self, request, *args, **kwargs):
        """Creates a new document type (manager only)."""
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
            "commission" in request.data
            and not request.user.has_perm("documents.add_document_any_commission")
            and not request.user.is_member_in_commission(request.data["commission"])
        ):
            return response.Response(
                {"error": _("Not allowed to create a document for this commission.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().create(request, *args, **kwargs)


class DocumentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/documents/{id} route"""

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    @extend_schema(
        responses={
            status.HTTP_200_OK: DocumentSerializer,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Retrieves a document type with all its details."""
        try:
            self.queryset.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Document does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        exclude=True,
        responses={
            status.HTTP_405_METHOD_NOT_ALLOWED: None,
        },
    )
    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(
        responses={
            status.HTTP_200_OK: DocumentSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    def patch(self, request, *args, **kwargs):
        try:
            self.queryset.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Document does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            "institution" in request.data
            and not request.user.has_perm("documents.change_document_any_institution")
            and not request.user.is_staff_in_institution(request.data["institution"])
        ):
            return response.Response(
                {"error": _("Not allowed to update a document for this institution.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "commission" in request.data
            and not request.user.has_perm("documents.change_document_any_commission")
            and not request.user.is_member_in_commission(request.data["commission"])
        ):
            return response.Response(
                {"error": _("Not allowed to update a document for this commission.")},
                status=status.HTTP_403_FORBIDDEN,
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
        try:
            document = self.queryset.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Document does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm(
            "documents.delete_document_any_institution"
        ) and not request.user.is_staff_in_institution(document.institution):
            return response.Response(
                {"error": _("Not allowed to delete a document for this institution.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not request.user.has_perm(
            "documents.delete_document_any_commission"
        ) and not request.user.is_member_in_commission(document.commission):
            return response.Response(
                {"error": _("Not allowed to delete a document for this commission.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        return self.destroy(request, *args, **kwargs)
