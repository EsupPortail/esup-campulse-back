from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.association import (
    AssociationAllDataReadSerializer,
)


class AssociationsCSVExport(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Association.objects.all()
    serializer_class = AssociationAllDataReadSerializer

    def get(self, request, *args, **kwargs):
        print("future CSV export view here")
        return response.Response(status=status.HTTP_200_OK)
