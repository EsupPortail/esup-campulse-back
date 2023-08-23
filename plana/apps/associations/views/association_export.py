"""Views directly linked to association exports."""
import csv

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.association import (
    AssociationAllDataReadSerializer,
)
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.institutions.models import Institution, InstitutionComponent
from plana.apps.users.models import GroupInstitutionFundUser
from plana.utils import generate_pdf


class AssociationDataExport(generics.RetrieveAPIView):
    """/associations/{id}/pdf_export route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Association.objects.all()
    serializer_class = AssociationAllDataReadSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: AssociationAllDataReadSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Retrieves a PDF file."""
        try:
            association = self.queryset.get(id=kwargs["pk"])
            data = association.__dict__
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Association does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            not request.user.has_perm("associations.view_association_not_enabled")
            and not request.user.has_perm("associations.view_association_not_public")
            and not request.user.is_president_in_association(association.id)
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this association.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        data["institution"] = Institution.objects.get(
            id=association.institution_id
        ).name
        data["institution_component"] = InstitutionComponent.objects.get(
            id=association.institution_component_id
        ).name
        data["activity_field"] = ActivityField.objects.get(
            id=association.activity_field_id
        ).name

        data["documents"] = list(
            DocumentUpload.objects.filter(
                association_id=data["id"],
                document_id__in=Document.objects.filter(
                    process_type__in=["CHARTER_ASSOCIATION", "DOCUMENT_ASSOCIATION"]
                ),
            ).values("name", "document__name")
        )

        return generate_pdf(
            data["name"],
            data,
            "association_charter_summary",
            request.build_absolute_uri("/"),
        )


class AssociationsCSVExport(generics.RetrieveAPIView):
    """/associations/csv_export route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Association.objects.all()
    serializer_class = AssociationAllDataReadSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "associations",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="IDs of selected associations, separated by a comma.",
            ),
        ],
        responses={
            status.HTTP_200_OK: AssociationAllDataReadSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Associations List CSV export."""
        associations = request.query_params.get("associations")

        if request.user.has_perm("associations.change_association_any_institution"):
            queryset = self.get_queryset()
        else:
            institutions = GroupInstitutionFundUser.objects.filter(
                user_id=request.user.id, institution_id__isnull=False
            ).values_list("institution_id")
            if len(institutions) == 0:
                return response.Response(
                    {"error": _("Not allowed to export associations list CSV.")},
                    status=status.HTTP_403_FORBIDDEN,
                )
            queryset = self.get_queryset().exclude(~Q(institution_id__in=institutions))

        if associations is not None and associations != "":
            association_ids = [
                int(association) for association in associations.split(",")
            ]
            queryset = queryset.exclude(~Q(id__in=association_ids))

        http_response = HttpResponse(content_type="application/csv")
        http_response[
            "Content-Disposition"
        ] = "Content-Disposition: attachment; filename=associations_export.csv"

        writer = csv.writer(http_response, delimiter=";")
        # Write column titles for the CSV file
        writer.writerow(
            [
                _("Name"),
                _("Acronym"),
                _("Institution"),
                _("Activity field"),
                _("Institution component"),
                _("Last GOA date"),
                _("Email"),
            ]
        )

        # Write CSV file content
        for association in queryset:
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
