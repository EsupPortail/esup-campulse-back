"""Serializers describing fields used on commissions."""
from rest_framework import serializers

from plana.apps.commissions.models.commission import Fund


class CommissionSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = Fund
        fields = "__all__"
