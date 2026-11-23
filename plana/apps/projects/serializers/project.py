"""Serializers describing fields used on projects."""

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from plana.apps.associations.serializers.association import AssociationMandatoryDataSerializer
from plana.apps.commissions.models import Commission
from plana.apps.commissions.serializers.commission import CommissionMinimalDataSerializer
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.projects.models.project import Project
from plana.apps.projects.serializers.category import CategorySerializer
from plana.apps.projects.serializers.project_commission_fund import ProjectCommissionFundMinimalDataSerializer
from plana.apps.projects.notifications import send_project_status_update_notification
from plana.apps.users.serializers.association_user import AssociationUserSerializer
from plana.apps.users.serializers.user import UserNameSerializer


class ProjectSerializer(serializers.ModelSerializer):
    """Main serializer."""

    categories = CategorySerializer(many=True, read_only=True)
    commission = CommissionMinimalDataSerializer(read_only=True)
    association = AssociationMandatoryDataSerializer(read_only=True)
    user = UserNameSerializer(read_only=True)
    association_user = AssociationUserSerializer(read_only=True)
    project_commission_funds = ProjectCommissionFundMinimalDataSerializer(many=True, read_only=True, source="projectcommissionfund_set")
    bearer_overdue_review_count = serializers.IntegerField(read_only=True)
    review_overdue_days = serializers.IntegerField(read_only=True)

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
            "commission",
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
            "project_commission_funds",
            "bearer_overdue_review_count",
            "review_overdue_days",
        ]


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """Main serializer without project_status."""

    categories = CategorySerializer(many=True, read_only=True)
    commission = CommissionMinimalDataSerializer(read_only=True)

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
            "commission",
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

    commission = CommissionMinimalDataSerializer(many=False, read_only=True)
    budget_file = serializers.SerializerMethodField("get_budget_file")
    association = AssociationMandatoryDataSerializer(read_only=True)
    user = UserNameSerializer(read_only=True)
    association_user = AssociationUserSerializer(read_only=True)
    project_commission_funds = ProjectCommissionFundMinimalDataSerializer(many=True, read_only=True, source="projectcommissionfund_set")
    review_overdue_days = serializers.IntegerField(read_only=True)

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
            "project_commission_funds",
            "review_overdue_days",
        ]


class ProjectStatusSerializer(serializers.ModelSerializer):
    """Serializer for status field."""
    project_status = serializers.ChoiceField(choices=Project.ProjectStatus.choices, required=True)

    class Meta:
        model = Project
        fields = ["project_status", "processing_date"]
        read_only_fields = ["processing_date"]

    def validate(self, data):
        request = self.context.get("request")
        project = self.instance

        old_project_status = project.project_status
        new_project_status = data["project_status"]

        # Must be updating to an authorized project status depending on user role
        authorized_statuses = []
        if request.user.has_perm("projects.change_project_as_bearer"):
            authorized_statuses += Project.ProjectStatus.get_bearer_project_statuses()
        if request.user.has_perm("projects.change_project_as_validator"):
            authorized_statuses += Project.ProjectStatus.get_validator_project_statuses()
        if new_project_status not in authorized_statuses:
            raise serializers.ValidationError({"forbidden_status": _("Choosing this status is not allowed.")})

        # Cannot change status for an archived project
        if old_project_status in Project.ProjectStatus.get_archived_project_statuses():
            raise serializers.ValidationError({"archived_project": _("Cannot change this project status anymore.")})

        # Check project status transition consistency
        if not project.can_transition_to_status(new_project_status):
            raise serializers.ValidationError({"status_inconsistency": _("Transition this project status to the one selected is not allowed.")})

        # Check if all requested documents were submitted to allow project status update
        if new_project_status in Project.ProjectStatus.get_bearer_project_statuses():
            if missing_documents_names := self._get_missing_documents_names(project, new_project_status):
                raise serializers.ValidationError({"missing_documents": _(f"Missing documents : {missing_documents_names}.")})

            # Setting up processing_date when new status need to
            if new_project_status in Project.ProjectStatus.get_email_project_processing_project_statuses():
                data["processing_date"] = timezone.now()

        return data

    def update(self, instance, validated_data):
        new_project_status = validated_data.get("project_status")
        # Giving project a manual identifier if needed
        if new_project_status in Project.ProjectStatus.get_identifier_project_statuses():
            instance.apply_manual_identifier()
        instance = super().update(instance, validated_data)
        # Mail sending to designated managers
        if new_project_status:
            send_project_status_update_notification(self.context.get("request"), instance)

        return instance

    @staticmethod
    def _get_missing_documents_names(project, new_project_status):
        document_process_types = (
            ["DOCUMENT_PROJECT"]
            if new_project_status in Project.ProjectStatus.get_email_project_processing_project_statuses()
            else ["DOCUMENT_PROJECT_REVIEW"]
            if new_project_status in Project.ProjectStatus.get_email_review_processing_project_statuses()
            else []
        )

        missing_documents = list(
            Document.objects.filter(
                models.Q(process_type__in=document_process_types)
                & (
                    models.Q(is_required_in_process=True, fund_id=None)
                    | models.Q(
                        is_required_in_process=True,
                        fund__commissionfund__projectcommissionfund__project_id=project.id,
                    )
                )
            ).exclude(documentupload__project=project)
        )
        return ", ".join(str(item) for item in missing_documents)


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
