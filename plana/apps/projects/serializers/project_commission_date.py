"""Serializers describing fields used on project commission date table."""
from rest_framework import serializers

from plana.apps.commissions.models.commission import Commission
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund


class ProjectCommissionDateSerializer(serializers.ModelSerializer):
    """Main serializer."""

    project = serializers.PrimaryKeyRelatedField(queryset=Project.visible_objects.all())
    commission_date = serializers.PrimaryKeyRelatedField(
        queryset=Commission.objects.all()
    )

    class Meta:
        model = ProjectCommissionFund
        fields = "__all__"


class ProjectCommissionDateDataSerializer(serializers.ModelSerializer):
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
            "commission_date_id",
            "project_id",
        ]
