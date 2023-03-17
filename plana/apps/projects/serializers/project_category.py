"""Serializers describing fields used on project category table."""
from rest_framework import serializers

from plana.apps.projects.models.category import Category
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory


class ProjectCategorySerializer(serializers.ModelSerializer):
    """Main serializer."""

    project = serializers.SlugRelatedField(
        slug_field="id", queryset=Project.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field="id", queryset=Category.objects.all()
    )

    class Meta:
        model = ProjectCategory
        fields = "__all__"
