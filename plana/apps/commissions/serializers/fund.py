"""Serializers describing fields used on commissions."""

from rest_framework import serializers

from plana.apps.commissions.models.fund import Fund


class FundSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = Fund
        fields = "__all__"
