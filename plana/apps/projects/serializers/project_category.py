"""Serializers describing fields used on project category table."""

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from plana.apps.projects.models.category import Category
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory


class ProjectCategorySerializer(serializers.ModelSerializer):
    """Main serializer for ProjectCategory model."""

    project = serializers.PrimaryKeyRelatedField(queryset=Project.visible_objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())

    def validate(self, data):
        """Custom validate to ensure the Project has only one Category linked to it, Category must be enabled"""
        project_categories = ProjectCategory.objects.filter(project_id=data.get("project"))
        if project_categories.exists():
            raise serializers.ValidationError({
                "already_existing_category": _("This project is already linked to a category. Only one is allowed per project.")
            })

        category = data.get("category")
        if category and not category.is_enabled:
            raise serializers.ValidationError({"category_disabled": _("A project cannot be linked to a disabled category.")})

        return data

    def create(self, validated_data):
        """ProjectCategory object creation should update the Project's edition date"""
        project = validated_data["project"]
        project.edition_date = timezone.now()
        project.save()
        return super().create(validated_data)

    class Meta:
        model = ProjectCategory
        fields = "__all__"
