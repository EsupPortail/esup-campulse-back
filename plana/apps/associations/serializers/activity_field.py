"""Serializers describing fields used on associations activity fields."""

from rest_framework import serializers

from plana.apps.associations.models.activity_field import ActivityField


class ActivityFieldSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = ActivityField
        fields = "__all__"
