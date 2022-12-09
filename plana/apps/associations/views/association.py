"""
Views directly linked to associations.
"""
from rest_framework import generics

from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.association import (
    AssociationListSerializer,
    AssociationRetrieveSerializer,
)


class AssociationList(generics.ListAPIView):
    """
    GET : Lists all associations currently active.
    """

    serializer_class = AssociationListSerializer
    queryset = Association.objects.filter(is_enabled=True).order_by("name")


class AssociationRetrieve(generics.RetrieveAPIView):
    """
    GET : Lists an association with all its details.
    """

    serializer_class = AssociationRetrieveSerializer
    queryset = Association.objects.all()
