"""
Serializers describing fields used on auth groups.
"""
from django.contrib.auth.models import Group

from rest_framework import serializers


class GroupSerializer(serializers.ModelSerializer):
    """
    Main serializer.
    """

    class Meta:
        model = Group
        fields = (
            "id",
            "name",
        )
