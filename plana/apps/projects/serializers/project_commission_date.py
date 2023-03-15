"""Serializers describing fields used on project commission date table."""
from rest_framework import serializers

from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.commissions.serializers.commission_date import CommissionDateSerializer
from plana.apps.projects.models.project import Project


class ProjectCommissionDateSerializer(serializers.ModelSerializer):
    """Main serializer."""

    project = serializers.SlugRelatedField(
        slug_field="id", queryset=Project.objects.all()
    )
    commission_date = CommissionDateSerializer()

    class Meta:
        model = ProjectCommissionDate
        fields = "__all__"
