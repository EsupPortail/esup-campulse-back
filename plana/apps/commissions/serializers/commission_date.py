"""Serializers describing fields used on commissions dates."""
from rest_framework import serializers

from plana.apps.commissions.models.commission_date import Commission


class CommissionDateSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = Commission
        fields = "__all__"


class CommissionDateUpdateSerializer(serializers.ModelSerializer):
    """Update serializer."""

    class Meta:
        model = Commission
        fields = ["submission_date", "commission_date"]
