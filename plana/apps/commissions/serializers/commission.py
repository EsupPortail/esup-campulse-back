"""Serializers describing fields used on commissions."""

import datetime

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from plana.apps.commissions.models.commission import Commission
from plana.utils import normalize_object_name


class CommissionSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = Commission
        fields = "__all__"


class CommissionUpdateSerializer(serializers.ModelSerializer):
    """Update serializer."""

    class Meta:
        model = Commission
        fields = ["submission_date", "commission_date", "name", "is_open_to_projects"]

    def validate(self, data):
        if data.get("name"):
            commissions = Commission.objects.all()
            for commission in commissions:
                if normalize_object_name(data["name"]) == normalize_object_name(commission.name):
                    raise serializers.ValidationError({"similar_name": _("Commission name already taken.")})

        commission_date = data.get("commission_date", self.instance.commission_date if self.instance.commission_date else None)
        submission_date = data.get("submission_date", self.instance.submission_date if self.instance.submission_date else None)
        if commission_date and submission_date:
            if submission_date < datetime.date.today():
                raise serializers.ValidationError({"past_date": _("Cannot create commission date taking place before today.")})
            if submission_date > commission_date:
                raise serializers.ValidationError({"inconsistent_dates": _("Can't set submission date after commission date.")})

        return data
