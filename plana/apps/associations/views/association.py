from rest_framework import generics

from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.association import (
    AssociationListSerializer,
    AssociationDetailSerializer,
)
# TODO Find a usage for that import, we need to import it to make migrations work.
from plana.apps.associations.serializers.social_network import SocialNetworkSerializer


class AssociationList(generics.ListAPIView):
    """
    GET : Lists all associations currently active.
    """

    serializer_class = AssociationListSerializer
    queryset = Association.objects.filter(is_enabled=True).order_by("name")


class AssociationDetail(generics.RetrieveAPIView):
    """
    GET : Lists an association with all its details.
    """

    serializer_class = AssociationDetailSerializer
    queryset = Association.objects.all()
