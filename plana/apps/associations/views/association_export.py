"""Views directly linked to association exports."""

from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.association import (
    AssociationAllDataReadSerializer,
)
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.users.models import GroupInstitutionFundUser
from plana.utils import generate_pdf_response
from ..filters import AssociationExportFilter
from ..utils import generate_associations_export

from plana.decorators import capture_queries


class AssociationListExport(generics.ListAPIView):
    """/associations/export route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Association.objects.all()
    serializer_class = AssociationAllDataReadSerializer
    filterset_class = AssociationExportFilter

    @extend_schema(
        operation_id="associations_export_list",
        parameters=[
            OpenApiParameter(
                "mode",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Export mode (xlsx or csv, csv by default).",
            ),
        ],
        responses={
            status.HTTP_200_OK: AssociationAllDataReadSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        },
    )
    @capture_queries()
    def get(self, request, *args, **kwargs):
        """Associations list export."""
        mode = request.query_params.get("mode")
        # associations = request.query_params.get("associations")

        institutions = GroupInstitutionFundUser.objects.filter(
            user_id=request.user.id, institution_id__isnull=False
        ).values_list("institution_id")
        if institutions.exists():
            return response.Response(
                {"error": _("Not allowed to export associations list CSV.")},
                status=status.HTTP_403_FORBIDDEN,
            )
        queryset = self.get_queryset().filter(institution_id__in=institutions)

        return generate_associations_export(queryset, mode)


class AssociationRetrieveExport(generics.RetrieveAPIView):
    """/associations/{id}/export route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Association.objects.all()
    serializer_class = AssociationAllDataReadSerializer

    @extend_schema(
        operation_id="associations_export_retrieve",
        responses={
            status.HTTP_200_OK: AssociationAllDataReadSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    @capture_queries()
    def get(self, request, *args, **kwargs):
        """Retrieve a PDF file."""
        association = self.get_object()
        data = association.__dict__

        if (
            not request.user.has_perm("associations.view_association_not_enabled")
            and not request.user.has_perm("associations.view_association_not_public")
            and not request.user.is_president_in_association(association.id)
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this association.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        data["institution"] = (
            association.institution.name
            if association.institution_id
            else None
        )
        data["institution_component"] = (
            association.institution_component.name
            if association.institution_component_id
            else None
        )
        data["activity_field"] = (
            association.activity_field.name
            if association.activity_field_id
            else None)

        data["documents"] = list(
            DocumentUpload.objects.filter(
                association_id=data["id"],
                document_id__in=Document.objects.filter(
                    process_type__in=["CHARTER_ASSOCIATION", "DOCUMENT_ASSOCIATION"]
                ),
            ).values("name", "document__name")
        )

        return generate_pdf_response(
            data["name"],
            data,
            "association_charter_summary",
            request.build_absolute_uri("/"),
        )
