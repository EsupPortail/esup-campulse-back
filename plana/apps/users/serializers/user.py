"""Serializers describing fields used on users and related forms."""

import re

from allauth.account.adapter import get_adapter
from django.conf import settings
from django.contrib.auth.models import Group
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import exceptions, serializers

from plana.apps.associations.serializers.association import (
    AssociationMandatoryDataSerializer,
)
from plana.apps.contents.models.setting import Setting
from plana.apps.users.models.user import AssociationUser, GroupInstitutionFundUser, User


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
        return user.is_cas_user

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
        return user.is_cas_user

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


############################
# REGISTRATION SERIALIZERS #
############################


class GroupInstitutionFundUserRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupInstitutionFundUser
        fields = ['group', 'institution', 'fund']

    def validate_group(self, value):
        if not settings.GROUPS_STRUCTURE.get(value.name, {}).get('REGISTRATION_ALLOWED'):
            raise exceptions.ValidationError(
                {"detail": [_("Registering in a private group is not allowed.")]}
            )
        return value

    def validate(self, data):
        if data.get('institution') and not settings.GROUPS_STRUCTURE.get(data['group'].name, {}).get('INSTITUTION_ID_POSSIBLE'):
            raise exceptions.ValidationError(
                {"detail": [_("Linking this institution to this group is not allowed.")]}
            )

        if data.get('fund') and not settings.GROUPS_STRUCTURE.get(data['group'].name, {}).get('FUND_ID_POSSIBLE'):
            raise exceptions.ValidationError(
                {"detail": [_("Linking this fund to this group is not allowed.")]}
            )
        return data


class AssociationUserRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = AssociationUser
        fields = [
            "association",
            "is_president",
            "is_vice_president",
            "is_secretary",
            "is_treasurer",
        ]


class CustomRegisterSerializer(serializers.ModelSerializer):
    """Used for the user registration form (to parse the phone field)."""

    phone = serializers.CharField(required=False, allow_blank=True, max_length=32)
    gifus = GroupInstitutionFundUserRegisterSerializer(many=True)
    associations = AssociationUserRegisterSerializer(many=True)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone", "gifus", "associations"]

    def validate_email(self, value):
        if value.split('@')[1] in Setting.get_setting("RESTRICTED_DOMAINS"):
            raise exceptions.ValidationError(
                {"detail": [_("This email address cannot be used to create a local account.")]}
            )
        return value

    def create_links(self, validated_data, user):
        """Create linked GIFU and AssociationUser objects"""

        gifus = validated_data.get('gifus', [])
        associations = validated_data.get('associations', [])

        gifus_list = []
        for gifu in gifus:
            try:
                gifus_list.append(GroupInstitutionFundUser.objects.create(user=user, **gifu))
            # Check the uniqueness of the GIFU
            except IntegrityError:
                raise serializers.ValidationError(
                    {"detail": [_("Cannot create a GroupInstitutionFundUser object that already exists.")]}
                )
        user.groupinstitutionfunduser_set.add(*gifus_list)

        asso_users_list = []
        self.validate_associations_users(associations, user)
        for asso in associations:
            self.validate_association_user(asso, user)
            try:
                asso_users_list.append(AssociationUser.objects.create(user=user, **asso))
            # Check the uniqueness of the AssociationUser
            except IntegrityError:
                raise serializers.ValidationError(
                    {"detail": [_("Cannot create an AssociationUser object that already exists.")]}
                )
        user.associationuser_set.add(*asso_users_list)
        return user

    def validate_associations_users(self, associations_data: list[dict], user):
        # At least one group can be linked to an association
        if not any(settings.GROUPS_STRUCTURE[group.name]["ASSOCIATIONS_POSSIBLE"]
                   for group in user.get_user_groups()):
            raise serializers.ValidationError(_("The user hasn't any group that can have associations."))

    def validate_association_user(self, association_data: dict, user):
        association = association_data['association']
        au_count = AssociationUser.objects.filter(association=association).count()
        if au_count >= association.amount_members_allowed:
            raise serializers.ValidationError(_("Too many users in association."))

        if (
            association_data.get('is_president')
            and AssociationUser.objects.filter(
                association=association, is_president=True
            ).exists()
        ):
            raise serializers.ValidationError(_("President already in association."))

    def save(self, request):
        """Save the user."""
        # self.cleaned_data = request.data
        self.cleaned_data = self.validated_data
        adapter = get_adapter()
        user = adapter.new_user(request)
        adapter.save_user(request, user, self)

        email = self.cleaned_data["email"]
        user.email = email.lower()
        user.username = email
        if "phone" in self.cleaned_data:
            user.phone = self.cleaned_data["phone"]

        user.save()
        self.create_links(self.cleaned_data, user)
        return user
