"""Serializers describing fields used on projects."""

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from plana.apps.associations.serializers.association import AssociationMandatoryDataSerializer
from plana.apps.commissions.models import Commission
from plana.apps.commissions.serializers.commission import CommissionSerializer
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.projects.models.project import Project
from plana.apps.projects.serializers.category import CategorySerializer
from plana.apps.users.serializers.association_user import AssociationUserSerializer
from plana.apps.users.serializers.user import UserNameSerializer


class ProjectSerializer(serializers.ModelSerializer):
    """Main serializer."""

    categories = CategorySerializer(many=True, read_only=True)
    commissions = CommissionSerializer(many=True, read_only=True)
    association = AssociationMandatoryDataSerializer(read_only=True)
    user = UserNameSerializer(read_only=True)
    association_user = AssociationUserSerializer(read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "manual_identifier",
            "planned_start_date",
            "planned_end_date",
            "planned_location",
            "user",
            "association",
            "association_user",
            "partner_association",
            "categories",
            "commissions",
            "budget_previous_edition",
            "target_audience",
            "amount_students_audience",
            "amount_all_audience",
            "ticket_price",
            "student_ticket_price",
            "individual_cost",
            "goals",
            "summary",
            "planned_activities",
            "prevention_safety",
            "marketing_campaign",
            "sustainable_development",
            "project_status",
            "creation_date",
            "edition_date",
            "processing_date",
        ]


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """Main serializer without project_status."""

    categories = CategorySerializer(many=True, read_only=True)
    commissions = CommissionSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "planned_start_date",
            "planned_end_date",
            "planned_location",
            "user",
            "association",
            "association_user",
            "partner_association",
            "categories",
            "commissions",
            "budget_previous_edition",
            "target_audience",
            "amount_students_audience",
            "amount_all_audience",
            "ticket_price",
            "student_ticket_price",
            "individual_cost",
            "goals",
            "summary",
            "planned_activities",
            "prevention_safety",
            "marketing_campaign",
            "sustainable_development",
        ]


class ProjectUpdateManagerSerializer(serializers.ModelSerializer):
    """Update serializer for manager."""

    class Meta:
        model = Project
        fields = [
            "planned_start_date",
            "planned_end_date",
        ]


class ProjectPartialDataSerializer(serializers.ModelSerializer):
    """Serializer for project list."""

    commission = CommissionSerializer(many=False, read_only=True)
    budget_file = serializers.SerializerMethodField("get_budget_file")
    association = AssociationMandatoryDataSerializer(read_only=True)
    user = UserNameSerializer(read_only=True)
    association_user = AssociationUserSerializer(read_only=True)

    @extend_schema_field(OpenApiTypes.STR)
    def get_budget_file(self, project):
        """Return a link to DocumentUploadFileRetrieve view for BUDGET_PREVISIONNEL."""
        try:
            budget_file = DocumentUpload.objects.get(
                document_id=Document.objects.get(acronym="BUDGET_PREVISIONNEL"), project_id=project.id
            )
            return reverse('document_upload_file_retrieve', args=[budget_file.id])
        except ObjectDoesNotExist:
            return None

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "manual_identifier",
            "association",
            "user",
            "association_user",
            "commission",
            "planned_start_date",
            "planned_end_date",
            "edition_date",
            "project_status",
            "budget_file",
        ]


class ProjectStatusSerializer(serializers.ModelSerializer):
    """Serializer for status field."""

    class Meta:
        model = Project
        fields = ["project_status", "processing_date"]


class ProjectPostponeSerializer(serializers.Serializer):
    """Serializer for project commission postpone"""
    new_commission_id = serializers.PrimaryKeyRelatedField(queryset=Commission.objects.all(), allow_null=False, required=True)

    def validate(self, data):
        project_id = self.context["view"].kwargs.get("project_id")
        eligible_commissions_ids = Commission.objects.allowing_project_postpone(project_id=project_id).values_list("id", flat=True)
        if data["new_commission_id"].pk not in eligible_commissions_ids:
            raise serializers.ValidationError({
                "commission_not_eligible": _("The selected commission is not eligible for this project postpone.")}
            )
        return data
