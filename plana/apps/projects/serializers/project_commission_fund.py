"""Serializers describing fields used on project commission fund table."""
from rest_framework import serializers

from plana.apps.commissions.models import CommissionFund
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund


class ProjectCommissionFundSerializer(serializers.ModelSerializer):
    """Main serializer."""

    project = serializers.PrimaryKeyRelatedField(queryset=Project.visible_objects.all())
    commission_fund = serializers.PrimaryKeyRelatedField(
        queryset=CommissionFund.objects.all()
    )

    class Meta:
        model = ProjectCommissionFund
        fields = "__all__"


class ProjectCommissionFundDataSerializer(serializers.ModelSerializer):
    """Fields that can be updated by project's bearer."""

    new_commission_fund_id = serializers.PrimaryKeyRelatedField(
        queryset=CommissionFund.objects.all(), required=False
    )

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
            "new_commission_fund_id",
            "project_id",
        ]
