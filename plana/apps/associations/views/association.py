"""
Views directly linked to associations.
"""
from django.utils.translation import ugettext_lazy as _

from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.association import (
    AssociationAllDataSerializer,
    AssociationPartialDataSerializer,
    AssociationMandatoryDataSerializer,
)


class AssociationListCreate(generics.ListCreateAPIView):
    """
    GET : Lists all associations currently active.

    POST : Creates a new association with mandatory informations.
    """

    queryset = Association.objects.filter(is_enabled=True).order_by("name")

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "POST":
            self.serializer_class = AssociationMandatoryDataSerializer
        else:
            self.serializer_class = AssociationPartialDataSerializer
        return super().get_serializer_class()

    def post(self, request, *args, **kwargs):
        if request.user.is_svu_manager:
            return super().create(request, *args, **kwargs)
        else:
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )


class AssociationRetrieve(generics.RetrieveAPIView):
    """
    GET : Lists an association with all its details.
    """

    serializer_class = AssociationAllDataSerializer
    queryset = Association.objects.all()
