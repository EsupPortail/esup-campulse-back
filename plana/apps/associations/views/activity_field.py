"""Views linked to associations activity fields."""

from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.serializers.activity_field import ActivityFieldSerializer


class AssociationActivityFieldList(generics.ListAPIView):
    """/associations/activity_fields route."""

    permission_classes = [AllowAny]
    queryset = ActivityField.objects.all().order_by("name")
    serializer_class = ActivityFieldSerializer
