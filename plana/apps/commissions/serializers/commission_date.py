"""Serializers describing fields used on commissions dates."""
from rest_framework import serializers

from plana.apps.commissions.models.commission_date import CommissionDate


class CommissionDateSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = CommissionDate
        fields = "__all__"


class CommissionDateUpdateSerializer(serializers.ModelSerializer):
    """Update serializer."""

    class Meta:
        model = CommissionDate
        fields = ["submission_date", "commission_date"]
