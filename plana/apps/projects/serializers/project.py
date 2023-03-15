"""Serializers describing fields used on projects."""
from rest_framework import serializers

from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate


class ProjectSerializer(serializers.ModelSerializer):
    """Main serializer."""

    categories = serializers.SerializerMethodField()
    first_edition = serializers.SerializerMethodField()
    amounts_previous_edition = serializers.SerializerMethodField()

    def get_categories(self, project):
        """Return project-category links."""
        return ProjectCategory.objects.filter(project_id=project.pk).values()

    def get_first_edition(self, project):
        """Return is_first_edition for every commission the project applied."""
        return ProjectCommissionDate.objects.filter(project_id=project.pk).values(
            "commission_date_id", "is_first_edition"
        )

    def get_amounts_previous_edition(self, project):
        return ProjectCommissionDate.objects.filter(project_id=project.pk).values(
            "commission_date_id",
            "amount_asked_previous_edition",
            "amount_earned_previous_edition",
        )

    class Meta:
        model = Project
        fields = [
            "name",
            "planned_start_date",
            "planned_end_date",
            "location",
            "user",
            "association",
            "categories",
            "first_edition",
            "amounts_previous_edition",
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
            "status",
        ]
