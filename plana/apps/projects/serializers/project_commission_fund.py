"""Serializers describing fields used on project commission fund table."""
import datetime

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from plana.apps.commissions.models import CommissionFund
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund
from plana.apps.projects.utils import send_pcf_notification_mail_with_attachments


class ProjectCommissionFundSerializer(serializers.ModelSerializer):
    """Main serializer."""

    project = serializers.PrimaryKeyRelatedField(queryset=Project.visible_objects.all())
    commission_fund = serializers.PrimaryKeyRelatedField(queryset=CommissionFund.objects.all())

    class Meta:
        model = ProjectCommissionFund
        fields = "__all__"


class ProjectCommissionFundDataSerializer(serializers.ModelSerializer):
    """Fields that can be updated by project's bearer."""

    class Meta:
        model = ProjectCommissionFund
        fields = [
            "is_first_edition",
            "amount_asked_previous_edition",
            "amount_earned_previous_edition",
            "amount_asked",
            "amount_earned",
            "is_validated_by_admin",
            "commission_fund_id",
            "project_id",
        ]

    def validate(self, data):
        request = self.context.get("request")
        # amount_earned and is_validated_by_admin are two fields used for different processes, should never be given together in workflow
        if "amount_earned" in data and "is_validated_by_admin" in data:
            raise serializers.ValidationError({"workflow_inconsistency": _("Cannot setup an admin validation and an amount earned at the same time.")})

        # Checking bearer and validator fields
        if (
            not request.user.has_perm("projects.change_projectcommissionfund_as_bearer")
            and (ProjectCommissionFund.get_bearer_fields() & data.keys())
        ):
            raise serializers.ValidationError({"forbidden_bearer_fields": _("Not allowed to update bearer fields for this project's commission.")})
        if (
            not request.user.has_perm("projects.change_projectcommissionfund_as_validator")
            and (ProjectCommissionFund.get_validator_fields() & data.keys())
        ):
            raise serializers.ValidationError({"forbidden_validator_fields": _("Not allowed to update validator fields for this project's commission.")})

        # Checking submission date
        commission = self.instance.commission_fund.commission
        if commission.submission_date < datetime.date.today() and not request.user.has_perm("projects.change_projectcommissionfund_as_validator"):
            raise serializers.ValidationError({"submission_date": _("Submission date for this commission is gone.")})

        return data

    def update(self, instance, validated_data):
        request = self.context.get("request")
        instance = super().update(instance, validated_data)
        # Sending notification emails to project owner and project managers
        if "amount_earned" in validated_data:
            notification_type = "REJECTION" if instance.amount_earned == 0 else "ATTRIBUTION"
            send_pcf_notification_mail_with_attachments(request=request, pcf=instance, notification_type=notification_type)
            instance.project.process_project_pcf_amount_earned_status_update()

        if "is_validated_by_admin" in validated_data:
            instance.project.process_project_pcf_admin_validation_status_update(request=request)

        return instance
