"""Serializers describing fields used on users and related forms."""

from rest_framework import serializers


class ExternalUserSerializer(serializers.Serializer):
    """External user serializer."""

    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    mail = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
