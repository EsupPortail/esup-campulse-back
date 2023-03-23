"""Views linked to associations activity fields."""

from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.serializers.activity_field import ActivityFieldSerializer


class AssociationActivityFieldList(generics.ListAPIView):
    """GET : Lists all activity fields."""

    permission_classes = [AllowAny]
    serializer_class = ActivityFieldSerializer

    def get_queryset(self):
        return ActivityField.objects.all().order_by("name")
