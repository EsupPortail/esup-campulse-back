"""Serializers describing fields used on commission funds."""

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from plana.apps.commissions.models import CommissionFund


class CommissionFundSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = CommissionFund
        fields = "__all__"

    def validate(self, data):
        commission_funds = CommissionFund.objects.filter(commission_id=data["commission"], fund_id=data["fund"]).exists()
        if commission_funds:
            raise serializers.ValidationError({"already_exists": _("This commission is already linked to this fund.")})
        return data
