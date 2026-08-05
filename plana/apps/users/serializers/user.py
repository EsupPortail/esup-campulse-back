"""Serializers describing fields used on users and related forms."""
import datetime
import re
import secrets
import string

from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.sites.shortcuts import get_current_site
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import exceptions, serializers

from plana.apps.associations.models import Association
from plana.apps.associations.serializers.association import (
    AssociationMandatoryDataSerializer,
)
from plana.apps.contents.models.setting import Setting
from plana.apps.users.models.user import AssociationUser, GroupInstitutionFundUser, User
from plana.apps.users.provider import CASProvider
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail, PHONE_REGEX_PATTERN


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
        return user.groupinstitutionfunduser_set.all().values_list('group__permissions__codename', flat=True)

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_groups(self, user):
        """Return groups-institutions-users links."""
        return user.groupinstitutionfunduser_set.values()

    def is_cas_user(self, user) -> bool:
        """Calculate field "is_cas" (True if user registered through CAS)."""
        if hasattr(user, 'is_cas_user_annot'):
            return user.is_cas_user_annot
        return user.is_cas_user

    def has_validated_email_user(self, user) -> bool:
        """Calculate field "has_validated_email" (True if user finished registration)."""
        if hasattr(user, 'has_validated_email_user_annot'):
            return user.has_validated_email_user_annot
        return user.has_validated_email_user

    def validate_phone(self, value):
        """Check phone field with a regex."""
        if value == '':
            return value
        if not re.match(PHONE_REGEX_PATTERN, value):
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
        if hasattr(user, 'is_cas_user_annot'):
            return user.is_cas_user_annot
        return user.is_cas_user

    def has_validated_email_user(self, user) -> bool:
        """Calculate field "has_validated_email" (True if user finished registration)."""
        if hasattr(user, 'has_validated_email_user_annot'):
            return user.has_validated_email_user_annot
        return user.has_validated_email_user

    def validate_phone(self, value):
        """Check phone field with a regex."""
        if value == '':
            return value
        if not re.match(PHONE_REGEX_PATTERN, value):
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

    def validate(self, data):
        if self.instance.is_cas_user:
            for restricted_field in ["email", "first_name", "last_name", "is_student", "username"]:
                data.pop(restricted_field, False)
        elif "email" in data:
            if data["email"].split('@')[1] in Setting.get_setting("RESTRICTED_DOMAINS"):
                raise serializers.ValidationError({"email_domain": _("This email address cannot be used for a local account.")})
            data["username"] = data["email"]
        return data


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
                {"gifu_institution": [_("Adding institution in this group is not possible.")]}
            )

        if data.get('fund') and not settings.GROUPS_STRUCTURE.get(data['group'].name, {}).get('FUND_ID_POSSIBLE'):
            raise exceptions.ValidationError(
                {"gifu_fund": [_("Adding fund in this group is not possible.")]}
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
    gifus = GroupInstitutionFundUserRegisterSerializer(many=True, write_only=True)
    associations = AssociationUserRegisterSerializer(many=True, write_only=True)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "phone", "gifus", "associations"]

    def validate(self, data):
        if data.get("email", "").split('@')[1] in Setting.get_setting("RESTRICTED_DOMAINS"):
            raise exceptions.ValidationError(
                {"email_domain": [_("This email address cannot be used to create a local account.")]}
            )
        return data

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
                    {"duplicate_gifu": [_("Cannot create a GroupInstitutionFundUser object that already exists.")]}
                )
        user.groupinstitutionfunduser_set.add(*gifus_list)

        if associations:
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
            raise serializers.ValidationError(
                {"associations_forbidden": _("The user hasn't any group that can have associations.")}
            )

    def validate_association_user(self, association_data: dict, user):
        association = association_data['association']

        if not association.is_enabled:
            raise serializers.ValidationError({"disabled_association": _("The selected association is not enabled for new applications.")})

        au_count = AssociationUser.objects.filter(association=association).count()
        if au_count >= association.amount_members_allowed:
            raise serializers.ValidationError({"too_many_members": _("Too many users in association.")})

        if (
            association_data.get('is_president')
            and AssociationUser.objects.filter(
                association=association, is_president=True
            ).exists()
        ):
            raise serializers.ValidationError({"president": _("President already in association.")})

    def save(self, request=None):
        """Save the user."""
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


class CustomCASDataRegisterSerializer(CustomRegisterSerializer):
    """
    Used for the CAS user registration form (to parse the phone field).
    Excluding CAS auto-filled fields
    """

    def get_fields(self):
        fields = super().get_fields()
        for field in ("last_name", "first_name", "email"):
            fields.pop(field, None)
        return fields

    def validate(self, data):
        return data

    def save(self, request=None):
        """Save the new data linked to CAS user."""
        self.cleaned_data = self.validated_data
        user = self.context.get("request").user if not request else request.user

        if "phone" in self.cleaned_data:
            user.phone = self.cleaned_data["phone"]

        user.save()
        self.create_links(self.cleaned_data, user)
        return user


class UserCreateSerializer(CustomRegisterSerializer):
    """
    Used for user creation from a manager user.
    """
    is_cas = serializers.BooleanField(write_only=True)

    class Meta(CustomRegisterSerializer.Meta):
        fields = CustomRegisterSerializer.Meta.fields + ["is_cas", "username"]

    def validate(self, data):
        if data.get("email", "").split('@')[1] in Setting.get_setting("RESTRICTED_DOMAINS") and not data.get("is_cas", False):
            raise exceptions.ValidationError(
                {"email_domain": _("This email address cannot be used to create a local account.")}
            )
        return data

    def validate_association_user(self, association_data: dict, user):
        association = association_data["association"]

        # TODO : authorized for manager ?
        if not association.is_enabled:
            raise serializers.ValidationError({"disabled_association": _("The selected association is not enabled for new applications.")})

        au_count = AssociationUser.objects.filter(association=association).count()
        if au_count >= association.amount_members_allowed:
            raise serializers.ValidationError({"too_many_members": _("Too many users in association.")})

        if (
            association_data.get('is_president')
            and AssociationUser.objects.filter(
                association=association, is_president=True
            ).exists()
        ):
            raise serializers.ValidationError({"president": _("President already in association.")})

        if Association.objects.managed_by_user(self.context.get("request").user).filter(pk=association_data["association"].id).exists():
            association_data["is_validated_by_admin"] = True

    def save(self, request=None):
        """Save the user."""
        self.cleaned_data = self.validated_data

        # Creating User and linked validated EmailAddress
        user_data = {k: v for k, v in self.cleaned_data.items() if k in [f.name for f in User._meta.fields]}
        user_data["username"] = self.cleaned_data["email"] if not self.cleaned_data["is_cas"] else self.cleaned_data["username"]
        user_data["is_validated_by_admin"] = True

        user = User.objects.create(**user_data)
        EmailAddress.objects.create(email=user.email, verified=True, primary=True, user_id=user.id)

        # Creating associated objects (GIFU, AssociationUser)
        self.create_links(self.cleaned_data, user)

        # Sending mail to created user
        # TODO : Simplify email sending process
        request = self.context.get("request")
        current_site = get_current_site(request)
        context = {
            "site_domain": current_site.domain,
            "site_name": current_site.name,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "manager_email_address": request.user.email,
            "documentation_url": Setting.get_setting("APP_DOCUMENTATION_URL"),
        }

        if not self.cleaned_data.get("is_cas"):
            password = "".join(
                secrets.choice(string.ascii_letters + string.digits) for i in range(settings.DEFAULT_PASSWORD_LENGTH)
            )
            user.set_password(password)
            user.password_last_change_date = datetime.datetime.today()
            user.save(update_fields=["password", "password_last_change_date"])
            context.update({
                "password": password,
                "password_change_url": f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_PASSWORD_CHANGE_PATH}"
            })
            template = MailTemplate.objects.get(code="USER_ACCOUNT_BY_MANAGER_CONFIRMATION")
        else:
            SocialAccount.objects.create(
                user=user,
                provider=CASProvider.id,
                uid=user.username,
                extra_data={},
            )
            template = MailTemplate.objects.get(code="USER_ACCOUNT_LDAP_BY_MANAGER_CONFIRMATION")

        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=self.cleaned_data["email"],
            subject=template.subject.replace("{{ site_name }}", context["site_name"]),
            message=template.parse_vars(request.user, request, context),
        )

        self.instance = user
        return user
