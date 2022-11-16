from rest_framework import generics

from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.association import AssociationSerializer


class AssociationList(generics.ListCreateAPIView):
    """
    GET : Lists all associations currently active.
    POST : Creates a new association.
    """

    serializer_class = AssociationSerializer

    def get_queryset(self):
        return Association.objects.filter(is_enabled=True).order_by("name")


class AssociationDetail(generics.RetrieveUpdateAPIView):
    """
    GET : Lists an association with all its details.
    PUT : Edits all fields of an association.
    PATCH : Edits one field of an association.
    """

    serializer_class = AssociationSerializer
    queryset = Association.objects.all()
