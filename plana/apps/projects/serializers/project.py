"""Serializers describing fields used on projects."""
from rest_framework import serializers

from plana.apps.commissions.serializers.commission import CommissionSerializer
from plana.apps.projects.models.project import Project
from plana.apps.projects.serializers.category import CategorySerializer


class ProjectSerializer(serializers.ModelSerializer):
    """Main serializer."""

    categories = CategorySerializer(many=True, read_only=True)
    commission_dates = CommissionSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "planned_start_date",
            "planned_end_date",
            "planned_location",
            "contact_first_name",
            "contact_last_name",
            "contact_email",
            "contact_phone",
            "user",
            "association",
            "categories",
            "commission_dates",
            "budget_previous_edition",
            "target_audience",
            "amount_students_audience",
            "amount_all_audience",
            "ticket_price",
            "individual_cost",
            "goals",
            "summary",
            "planned_activities",
            "prevention_safety",
            "marketing_campaign",
            "project_status",
            "creation_date",
            "edition_date",
        ]


class ProjectReviewSerializer(serializers.ModelSerializer):
    """Main review serializer."""

    commission_dates = CommissionSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "planned_start_date",
            "planned_end_date",
            "planned_location",
            "contact_first_name",
            "contact_last_name",
            "contact_email",
            "contact_phone",
            "user",
            "association",
            "commission_dates",
            "outcome",
            "income",
            "real_start_date",
            "real_end_date",
            "real_location",
            "review",
            "impact_students",
            "description",
            "difficulties",
            "improvements",
            "creation_date",
            "edition_date",
        ]


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """Main serializer without project_status."""

    name = serializers.CharField(required=False, allow_blank=True)
    contact_first_name = serializers.CharField(required=False, allow_blank=True)
    contact_last_name = serializers.CharField(required=False, allow_blank=True)
    contact_email = serializers.CharField(required=False, allow_blank=True)
    contact_phone = serializers.CharField(required=False, allow_blank=True)
    categories = CategorySerializer(many=True, read_only=True)
    commission_dates = CommissionSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "planned_start_date",
            "planned_end_date",
            "planned_location",
            "contact_first_name",
            "contact_last_name",
            "contact_email",
            "contact_phone",
            "user",
            "association",
            "categories",
            "commission_dates",
            "budget_previous_edition",
            "target_audience",
            "amount_students_audience",
            "amount_all_audience",
            "ticket_price",
            "individual_cost",
            "goals",
            "summary",
            "planned_activities",
            "prevention_safety",
            "marketing_campaign",
        ]


class ProjectUpdateManagerSerializer(serializers.ModelSerializer):
    """Update serializer for manager."""

    class Meta:
        model = Project
        fields = [
            "planned_start_date",
            "planned_end_date",
        ]


class ProjectReviewUpdateSerializer(serializers.ModelSerializer):
    """Main review serializer for update."""

    contact_first_name = serializers.CharField(required=False, allow_blank=True)
    contact_last_name = serializers.CharField(required=False, allow_blank=True)
    contact_email = serializers.CharField(required=False, allow_blank=True)
    contact_phone = serializers.CharField(required=False, allow_blank=True)
    commission_dates = CommissionSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "contact_first_name",
            "contact_last_name",
            "contact_email",
            "contact_phone",
            "commission_dates",
            "outcome",
            "income",
            "real_start_date",
            "real_end_date",
            "real_location",
            "review",
            "impact_students",
            "description",
            "difficulties",
            "improvements",
        ]


class ProjectPartialDataSerializer(serializers.ModelSerializer):
    """Serializer for project list."""

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "association",
            "user",
            "edition_date",
            "project_status",
        ]


class ProjectStatusSerializer(serializers.ModelSerializer):
    """Serializer for status field."""

    class Meta:
        model = Project
        fields = ["project_status"]
