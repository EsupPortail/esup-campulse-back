"""Serializers describing fields used on users and related forms."""

import re

from allauth.account.adapter import get_adapter
from django.conf import settings
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import exceptions, serializers

from plana.apps.associations.serializers.association import (
    AssociationMandatoryDataSerializer,
)
from plana.apps.users.models.user import GroupInstitutionFundUser, User


class UserSerializer(serializers.ModelSerializer):
    """Main serializer."""

    address = serializers.CharField(required=False, allow_blank=True)
    zipcode = serializers.CharField(required=False, allow_blank=True, max_length=32)
    city = serializers.CharField(required=False, allow_blank=True, max_length=128)
    country = serializers.CharField(required=False, allow_blank=True, max_length=128)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=32)
    is_cas = serializers.SerializerMethodField("is_cas_user")
    has_validated_email = serializers.SerializerMethodField("has_validated_email_user")
    associations = AssociationMandatoryDataSerializer(many=True, read_only=True)
    groups = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_permissions(self, user):
        """Return permissions linked to the user."""
        permissions = []
        groups = Group.objects.filter(
            id__in=GroupInstitutionFundUser.objects.filter(user_id=user.id).values_list("group_id")
        )
        for group in groups:
            permissions = [
                *permissions,
                *group.permissions.values_list("codename", flat=True),
            ]
        return permissions
        # return user.get_group_permissions()

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_groups(self, user):
        """Return groups-institutions-users links."""
        return GroupInstitutionFundUser.objects.filter(user_id=user.id).values()

    def is_cas_user(self, user) -> bool:
        """Calculate field "is_cas" (True if user registered through CAS)."""
        return user.is_cas_user()

    def has_validated_email_user(self, user) -> bool:
        """Calculate field "has_validated_email" (True if user finished registration)."""
        return user.has_validated_email_user()

    def validate_phone(self, value):
        """Check phone field with a regex."""
        if value == '':
            return value
        pattern = r"^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError("Wrong phone number format.")
        return value

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "address",
            "zipcode",
            "city",
            "country",
            "phone",
            "is_cas",
            "has_validated_email",
            "is_validated_by_admin",
            "is_student",
            "can_submit_projects",
            "associations",
            "groups",
            "permissions",
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer to patch the user."""

    username = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    email = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    zipcode = serializers.CharField(required=False, allow_blank=True, max_length=32)
    city = serializers.CharField(required=False, allow_blank=True, max_length=128)
    country = serializers.CharField(required=False, allow_blank=True, max_length=128)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=32)
    is_cas = serializers.SerializerMethodField("is_cas_user")
    has_validated_email = serializers.SerializerMethodField("has_validated_email_user")
    associations = AssociationMandatoryDataSerializer(many=True, read_only=True)
    groups = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_permissions(self, user):
        """Return permissions linked to the user."""
        permissions = []
        groups = Group.objects.filter(
            id__in=GroupInstitutionFundUser.objects.filter(user_id=user.id).values_list("group_id")
        )
        for group in groups:
            permissions = [
                *permissions,
                *group.permissions.values_list("codename", flat=True),
            ]
        return permissions
        # return user.get_group_permissions()

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_groups(self, user):
        """Return groups-institutions-users links."""
        return GroupInstitutionFundUser.objects.filter(user_id=user.id).values()

    def is_cas_user(self, user) -> bool:
        """Calculate field "is_cas" (True if user registered through CAS)."""
        return user.is_cas_user()

    def has_validated_email_user(self, user) -> bool:
        """Calculate field "has_validated_email" (True if user finished registration)."""
        return user.has_validated_email_user()

    def validate_phone(self, value):
        """Check phone field with a regex."""
        if value == '':
            return value
        pattern = r"^[+]?[(]?[0-9]{3}[)]?[-\s.]?[0-9]{3}[-\s.]?[0-9]{4,6}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError("Wrong phone number format.")
        return value

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "address",
            "zipcode",
            "city",
            "country",
            "phone",
            "is_cas",
            "has_validated_email",
            "is_validated_by_admin",
            "is_student",
            "can_submit_projects",
            "associations",
            "groups",
            "permissions",
        ]


class UserPartialDataSerializer(serializers.ModelSerializer):
    """Used to get data from another student in the same associations."""

    is_cas = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "phone",
            "email",
            "is_cas",
            "is_validated_by_admin",
        ]


class UserNameSerializer(serializers.ModelSerializer):
    """Used to get data from another student in the same associations."""

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
        ]


class CustomRegisterSerializer(serializers.ModelSerializer):
    """Used for the user registration form (to parse the phone field)."""

    phone = serializers.CharField(required=False, allow_blank=True, max_length=32)

    def save(self, request):
        """Save the user."""
        self.cleaned_data = request.data
        if self.cleaned_data["email"].split('@')[1] in settings.RESTRICTED_DOMAINS:
            raise exceptions.ValidationError(
                {"detail": [_("This email address cannot be used to create a local account.")]}
            )
        adapter = get_adapter()
        user = adapter.new_user(request)
        adapter.save_user(request, user, self)

        user.email = self.cleaned_data["email"].lower()
        user.username = self.cleaned_data["email"]
        if "phone" in self.cleaned_data:
            user.phone = self.cleaned_data["phone"]

        user.save()
        return user

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone"]
