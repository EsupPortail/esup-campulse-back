"""Serializers describing fields used on users and related forms."""
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
from plana.apps.users.models.user import GroupInstitutionCommissionUser, User


class UserSerializer(serializers.ModelSerializer):
    """Main serializer."""

    address = serializers.CharField(required=False, allow_blank=True)
    zipcode = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
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
            id__in=GroupInstitutionCommissionUser.objects.filter(
                user_id=user.id
            ).values_list("group_id")
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
        return GroupInstitutionCommissionUser.objects.filter(user_id=user.id).values()

    def is_cas_user(self, user) -> bool:
        """Calculate field "is_cas" (True if user registered through CAS)."""
        return user.is_cas_user()

    def has_validated_email_user(self, user) -> bool:
        """Calculate field "has_validated_email" (True if user finished registration)."""
        return user.has_validated_email_user()

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
            "phone",
            "is_cas",
            "has_validated_email",
            "is_validated_by_admin",
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
            "is_cas",
            "is_validated_by_admin",
        ]


class CustomRegisterSerializer(serializers.ModelSerializer):
    """Used for the user registration form (to parse the phone field)."""

    phone = serializers.CharField(required=False, allow_blank=True)

    """
    def get_validation_exclusions(self):
        exclusions = super(CustomRegisterSerializer, self).get_validation_exclusions()
        return exclusions + ["phone"]
    """

    """
    def validate_email(self, value):
        ModelClass = self.Meta.model
        if ModelClass.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                _("This email address is already in use.")
            )
        return value
    """

    def save(self, request):
        self.cleaned_data = request.data
        if self.cleaned_data["email"].split('@')[1] in settings.RESTRICTED_DOMAINS:
            raise exceptions.ValidationError(
                {
                    "detail": [
                        _(
                            "This email address cannot be used to create a local account."
                        )
                    ]
                }
            )
        adapter = get_adapter()
        user = adapter.new_user(request)
        adapter.save_user(request, user, self)

        user.username = self.cleaned_data["email"]
        if "phone" in self.cleaned_data:
            user.phone = self.cleaned_data["phone"]

        user.save()
        return user

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone"]
