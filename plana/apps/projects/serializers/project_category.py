"""Serializers describing fields used on project category table."""
from rest_framework import serializers

from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory
from plana.apps.projects.serializers.category import CategorySerializer


class ProjectCategorySerializer(serializers.ModelSerializer):
    """Main serializer."""

    project = serializers.SlugRelatedField(
        slug_field="id", queryset=Project.objects.all()
    )
    category = CategorySerializer()

    class Meta:
        model = ProjectCategory
        fields = "__all__"
