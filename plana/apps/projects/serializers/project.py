"""Serializers describing fields used on projects."""
from rest_framework import serializers

from plana.apps.projects.models.project import Project


class ProjectSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = Project
        fields = "__all__"
