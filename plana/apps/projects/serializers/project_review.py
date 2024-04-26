"""Serializers describing fields used on project reviews."""

from rest_framework import serializers

from plana.apps.commissions.serializers.commission import CommissionSerializer
from plana.apps.projects.models.project import Project


class ProjectReviewSerializer(serializers.ModelSerializer):
    """Main review serializer."""

    commissions = CommissionSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "planned_start_date",
            "planned_end_date",
            "planned_location",
            "user",
            "association",
            "association_user",
            "commissions",
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


class ProjectReviewUpdateSerializer(serializers.ModelSerializer):
    """Main review serializer for update."""

    commissions = CommissionSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "association_user",
            "commissions",
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
