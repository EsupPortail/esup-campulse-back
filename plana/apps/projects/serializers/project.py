"""Serializers describing fields used on projects."""
from rest_framework import serializers

from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory


class ProjectSerializer(serializers.ModelSerializer):
    """Main serializer."""

    categories = serializers.SerializerMethodField()

    def get_categories(self, project):
        """Return project-category links."""
        return ProjectCategory.objects.filter(project_id=project.pk).values()

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
            "target_audience",
            "type_target_audience",
            "amount_target_audience",
            "amount_students_target_audience",
            "ticket_price",
            "individual_cost",
        ]
