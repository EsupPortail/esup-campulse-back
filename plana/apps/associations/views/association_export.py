import csv

from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.association import (
    AssociationAllDataReadSerializer,
)
from plana.apps.institutions.models import Institution, InstitutionComponent


class AssociationsCSVExport(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Association.objects.all()
    serializer_class = AssociationAllDataReadSerializer

    def get(self, request, *args, **kwargs):
        http_response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="associations.csv"'},
        )
        writer = csv.writer(http_response)
        writer.writerow(
            [
                _("Name"),
                _("Acronym"),
                _("Institution"),
                _("Activity Field"),
                _("Institution Component"),
                _("Last GOA Date"),
                _("Email"),
            ]
        )
        for association in self.get_queryset():
            institution_component = (
                None
                if association.institution_component_id is None
                else InstitutionComponent.objects.get(
                    id=association.institution_component_id
                ).name
            )
            writer.writerow(
                [
                    association.name,
                    association.acronym,
                    Institution.objects.get(id=association.institution_id).name,
                    association.activity_field,
                    institution_component,
                    association.last_goa_date,
                    association.email,
                ]
            )
        return http_response
