from rest_framework import generics

from .serializers import AssociationSerializer
from .models import Association


class AssociationList(generics.ListCreateAPIView):
    """
    GET : Lists all associations currently active.
    POST : Creates a new association.
    """

    serializer_class = AssociationSerializer

    def get_queryset(self):
        return Association.objects.filter(is_enabled=True).order_by("name")


class AssociationDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GET : Lists an association with all its details.
    PUT : Edits all fields of an association.
    PATCH : Edits one field of an association.
    DELETE : Deletes an association.
    """

    serializer_class = AssociationSerializer
    queryset = Association.objects.all()
