"""
Views directly linked to associations.
"""
import unicodedata

from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.association import (
    AssociationAllDataSerializer,
    AssociationMandatoryDataSerializer,
    AssociationPartialDataSerializer,
)


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                "is_enabled",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter for non-validated associations.",
            ),
            OpenApiParameter(
                "is_site",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter for associations from site.",
            ),
        ]
    )
)
class AssociationListCreate(generics.ListCreateAPIView):
    """
    GET : Lists all associations currently active.

    POST : Creates a new association with mandatory informations.
    """

    def get_queryset(self):
        queryset = Association.objects.all().order_by("name")
        if self.request.method == "GET":
            booleans = {"true": True, "false": False}
            is_enabled = self.request.query_params.get("is_enabled")
            is_site = self.request.query_params.get("is_site")
            if is_enabled is not None:
                queryset = queryset.filter(is_enabled=booleans.get(is_enabled))
            if is_site is not None:
                queryset = queryset.filter(is_site=booleans.get(is_site))
        return queryset

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
            try:
                association_name = request.data["name"]
            except KeyError:
                return response.Response(
                    {"error": _("Bad request.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Removes spaces, uppercase and accented characters to avoid similar association names.
            new_association_name = (
                unicodedata.normalize(
                    "NFD", association_name.strip().replace(" ", "").lower()
                )
                .encode("ascii", "ignore")
                .decode("utf-8")
            )
            associations = Association.objects.all()
            for association in associations:
                existing_association_name = (
                    unicodedata.normalize(
                        "NFD", association.name.strip().replace(" ", "").lower()
                    )
                    .encode("ascii", "ignore")
                    .decode("utf-8")
                )
                if new_association_name == existing_association_name:
                    return response.Response(
                        {"error": _("Association name already taken.")},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            return super().create(request, *args, **kwargs)
        else:
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )


class AssociationRetrieveDestroy(generics.RetrieveDestroyAPIView):
    """
    GET : Lists an association with all its details.

    DELETE : Removes an entire association.
    """

    serializer_class = AssociationAllDataSerializer
    queryset = Association.objects.all()

    def delete(self, request, *args, **kwargs):
        if not request.user.is_anonymous and request.user.is_svu_manager:
            return self.destroy(request, *args, **kwargs)
        return response.Response(
            {"error": _("Bad request.")},
            status=status.HTTP_403_FORBIDDEN,
        )
