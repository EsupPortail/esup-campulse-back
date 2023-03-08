"""Serializers describing fields used on commissions."""
from rest_framework import serializers

from plana.apps.commissions.models.commission import Commission


class CommissionSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = Commission
        fields = "__all__"
