"""Serializers describing fields used on project commission date table."""
from rest_framework import serializers

from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate


class ProjectCommissionDateSerializer(serializers.ModelSerializer):
    """Complete serializer."""

    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())
    commission_date = serializers.PrimaryKeyRelatedField(
        queryset=CommissionDate.objects.all()
    )

    class Meta:
        model = ProjectCommissionDate
        fields = "__all__"


class ProjectCommissionDateDataSerializer(serializers.ModelSerializer):
    """Only data serializer."""

    class Meta:
        model = ProjectCommissionDate
        fields = [
            "is_first_edition",
            "amount_asked_previous_edition",
            "amount_earned_previous_edition",
            "amount_asked",
            "amount_earned",
        ]
