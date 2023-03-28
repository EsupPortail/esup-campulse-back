"""Views directly linked to documents."""

from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
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

    def get(self, request, *args, **kwargs):
        """Lists all documents types."""
        return self.list(request, *args, **kwargs)

    # TODO: add permission add_document_any_institution + unittests
    def post(self, request, *args, **kwargs):
        """Creates a new document type (manager only)."""
        if not request.user.has_perm("documents.add_document"):
            return response.Response(
                {"error": _("Not allowed to add a new document type.")},
                status=status.HTTP_403_FORBIDDEN,
            )
        elif request.user.get_user_institutions().count() == 1:
            request.data["institution"] = (
                request.user.get_user_institutions().first().id
            )

        return super().create(request, *args, **kwargs)


class DocumentRetrieveDestroy(generics.RetrieveDestroyAPIView):
    """/documents/{id} route"""

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        """Retrieves a document type with all its details."""
        try:
            document_id = kwargs["pk"]
            self.queryset.get(id=document_id)
        except (ObjectDoesNotExist, MultiValueDictKeyError):
            return response.Response(
                {"error": _("No document id given.")},
                status=status.HTTP_404_NOT_FOUND,
            )
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Destroys an entire document type (manager only)."""
        try:
            document_id = kwargs["pk"]
            document = self.queryset.get(id=document_id)
        except (ObjectDoesNotExist, MultiValueDictKeyError):
            return response.Response(
                {"error": _("No document id given.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        # TODO: permissions for documents linked to a commission
        if not request.user.has_perm(
            "documents.delete_document_any_institution"
        ) and not request.user.is_staff_in_institution(document.institution):
            return response.Response(
                {"error": _("Not allowed to delete a document for this institution.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        return self.destroy(request, *args, **kwargs)
