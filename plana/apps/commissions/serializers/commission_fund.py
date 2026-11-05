"""Serializers describing fields used on commission funds."""

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from plana.apps.commissions.models import CommissionFund
from plana.apps.commissions.serializers.commission import CommissionMinimalDataSerializer
from plana.apps.commissions.serializers.fund import FundMinimalDataSerializer


class CommissionFundSerializer(serializers.ModelSerializer):
    """Main serializer."""
    commission = CommissionMinimalDataSerializer(read_only=True)
    fund = FundMinimalDataSerializer(read_only=True)

    class Meta:
        model = CommissionFund
        fields = "__all__"

    def validate(self, data):
        commission_funds = CommissionFund.objects.filter(commission_id=data["commission"], fund_id=data["fund"]).exists()
        if commission_funds:
            raise serializers.ValidationError({"already_exists": _("This commission is already linked to this fund.")})
        return data

    def create(self, validated_data):
        """CommissionFund object creation should update the Commission's edition date"""
        commission = validated_data["commission"]
        commission.edition_date = timezone.now()
        commission.save()
        return super().create(validated_data)
