"""Serializers describing fields used on commission funds."""
from rest_framework import serializers

from plana.apps.commissions.models import CommissionFund


class CommissionFundSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = CommissionFund
        fields = "__all__"
