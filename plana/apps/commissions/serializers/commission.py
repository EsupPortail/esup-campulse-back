"""Serializers describing fields used on commissions."""

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from plana.apps.commissions.models import Fund
from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.serializers.fund import FundMinimalDataSerializer
from plana.utils import normalize_object_name


class CommissionSerializer(serializers.ModelSerializer):
    """Main serializer."""
    funds = serializers.SerializerMethodField()

    def get_funds(self, obj) -> list[dict]:
        funds = Fund.objects.filter(commissionfund__commission=obj)
        return FundMinimalDataSerializer(funds, many=True, context=self.context).data

    class Meta:
        model = Commission
        fields = "__all__"


class CommissionManageSerializer(serializers.ModelSerializer):
    """Main serializer."""
    funds = serializers.SerializerMethodField()
    submitted_projects_count = serializers.IntegerField(read_only=True, default=None)
    processing_projects_count = serializers.IntegerField(read_only=True, default=None)
    standby_projects_count = serializers.IntegerField(read_only=True, default=None)
    overdue_review_count = serializers.IntegerField(read_only=True, default=None)

    def get_funds(self, obj) -> list[dict]:
        funds = Fund.objects.filter(commissionfund__commission=obj)
        return FundMinimalDataSerializer(funds, many=True, context=self.context).data

    class Meta:
        model = Commission
        fields = "__all__"
        read_only_fields = ["is_archived"]

    def validate_name(self, value):
        normalized_value = value.strip().replace(" ", "")
        name_exists = Commission.objects.filter(name__nospaces__unaccent=normalized_value).exists()
        if name_exists:
            raise serializers.ValidationError({"name": _("Commission name already taken.")})
        return value

    def validate(self, data):
        today = timezone.localdate()
        submission_date = data.get("submission_date")
        commission_date = data.get("commission_date")
        edition_date = data.get("edition_date")

        if submission_date and submission_date < today:
            raise serializers.ValidationError({"submission_date": _("Cannot create commission date taking place before today.")})
        if submission_date and commission_date and submission_date > commission_date:
            raise serializers.ValidationError({"inconsistent_dates": _("Can't set submission date after commission date.")})

        if edition_date and submission_date and edition_date <= submission_date:
            raise serializers.ValidationError({"too_early_edition_date": _("The edition date must be later than the submission date.")})
        if edition_date and commission_date and edition_date > commission_date:
            raise serializers.ValidationError({"too_late_edition_date": _("The edition date must be earlier than or equal to the commission date.")})

        return data


class CommissionMinimalDataSerializer(serializers.ModelSerializer):
    """Commission serializer with fewer data."""

    class Meta:
        model = Commission
        fields = "__all__"


class CommissionUpdateSerializer(serializers.ModelSerializer):
    """Update serializer."""

    class Meta:
        model = Commission
        fields = [
            "submission_date",
            "commission_date",
            "name",
            "is_open_to_projects",
            "edition_date",
            "room",
            "building",
            "address",
            "scheduled_time"
        ]

    def validate(self, data):
        if data.get("name"):
            commissions = Commission.objects.all()
            for commission in commissions:
                if normalize_object_name(data["name"]) == normalize_object_name(commission.name):
                    raise serializers.ValidationError({"similar_name": _("Commission name already taken.")})

        today = timezone.localdate()
        commission_date = data.get("commission_date", self.instance.commission_date if self.instance.commission_date else None)
        submission_date = data.get("submission_date", self.instance.submission_date if self.instance.submission_date else None)
        edition_date = data.get("edition_date", self.instance.edition_date if self.instance.edition_date else None)
        if commission_date and submission_date:
            if submission_date < today:
                raise serializers.ValidationError({"past_date": _("Cannot create commission date taking place before today.")})
            if submission_date > commission_date:
                raise serializers.ValidationError({"inconsistent_dates": _("Can't set submission date after commission date.")})

            if edition_date:
                if edition_date <= submission_date:
                    raise serializers.ValidationError({"too_early_edition_date": _("The edition date must be later than the submission date.")})
                if edition_date > commission_date:
                    raise serializers.ValidationError({"too_late_edition_date": _("The edition date must be earlier than or equal to the commission date.")})

        return data
