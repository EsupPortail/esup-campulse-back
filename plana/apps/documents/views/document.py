"""Views directly linked to documents."""
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.documents.models.document import Document
from plana.apps.documents.serializers.document import DocumentSerializer


class DocumentList(generics.ListAPIView):
    """Lists all Documents."""

    serializer_class = DocumentSerializer

    def get_queryset(self):
        """GET : Lists all documents."""
        return Document.objects.all()


class DocumentRetrieveDestroy(generics.RetrieveDestroyAPIView):
    """
    GET : Lists a document type with all its details.

    DELETE : Removes an entire document type.
    """

    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get_permissions(self):
        if self.request.method in ("DELETE"):
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        try:
            document_id = kwargs["pk"]
            document = self.queryset.get(id=document_id)
        except (ObjectDoesNotExist, MultiValueDictKeyError):
            return response.Response(
                {"error": _("No document id given.")},
                status=status.HTTP_404_NOT_FOUND,
            )
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        try:
            document_id = kwargs["pk"]
            document = self.queryset.get(id=document_id)
        except (ObjectDoesNotExist, MultiValueDictKeyError):
            return response.Response(
                {"error": _("No document id given.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        # TODO: define proper permissions to delete a document type
        #        if not request.user.has_perm(
        #            "associations.delete_association_any_institution"
        #        ) and not request.user.is_staff_in_institution(association.institution):
        #            return response.Response(
        #                {
        #                    "error": _(
        #                        "Not allowed to delete an association for this institution."
        #                    )
        #                },
        #                status=status.HTTP_403_FORBIDDEN,
        #            )

        return self.destroy(request, *args, **kwargs)
