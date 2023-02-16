"""
Serializers describing fields used on users and related forms.
"""
from allauth.account.adapter import get_adapter
from dj_rest_auth.serializers import (
    PasswordChangeSerializer as DJRestAuthPasswordChangeSerializer,
)
from dj_rest_auth.serializers import (
    PasswordResetConfirmSerializer as DJRestAuthPasswordResetConfirmSerializer,
)
from dj_rest_auth.serializers import (
    PasswordResetSerializer as DJRestAuthPasswordResetSerializer,
)
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


class ExternalUserSerializer(serializers.Serializer):
    """External user serializer."""

    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    mail = serializers.CharField(required=False)
