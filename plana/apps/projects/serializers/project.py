"""Serializers describing fields used on projects."""
from rest_framework import serializers

from plana.apps.commissions.serializers.commission_date import CommissionDateSerializer
from plana.apps.projects.models.project import Project
from plana.apps.projects.serializers.category import CategorySerializer


class ProjectSerializer(serializers.ModelSerializer):
    """Main serializer."""

    categories = CategorySerializer(many=True, read_only=True)
    commission_dates = CommissionDateSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "planned_start_date",
            "planned_end_date",
            "location",
            "user",
            "association",
            "categories",
            "commission_dates",
            "budget_previous_edition",
            "target_audience",
            "type_target_audience",
            "amount_target_audience",
            "amount_students_target_audience",
            "ticket_price",
            "individual_cost",
            "goals",
            "summary",
            "planned_activities",
            "prevention_safety",
            "marketing_campaign",
            "project_status",
        ]


class ProjectPartialDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "association", "user", "edition_date", "project_status"]


class ProjectRestrictedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["project_status"]
