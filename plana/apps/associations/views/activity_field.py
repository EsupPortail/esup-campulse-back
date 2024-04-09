"""Views linked to associations activity fields."""

from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.serializers.activity_field import ActivityFieldSerializer


class AssociationActivityFieldList(generics.ListAPIView):
    """/associations/activity_fields route."""

    permission_classes = [AllowAny]
    queryset = ActivityField.objects.all().order_by("name")
    serializer_class = ActivityFieldSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: ActivityFieldSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """List all activity fields that can be linked to an association."""
        return self.list(request, *args, **kwargs)
