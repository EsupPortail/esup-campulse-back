from rest_framework import exceptions, serializers

from allauth.account.adapter import get_adapter
from dj_rest_auth.serializers import (
    PasswordChangeSerializer as DJRestAuthPasswordChangeSerializer,
    PasswordResetSerializer as DJRestAuthPasswordResetSerializer,
)

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from plana.apps.users.models.user import User, AssociationUsers
from plana.apps.groups.serializers.group import GroupSerializer
from plana.apps.associations.serializers.association import (
    SimpleAssociationDataSerializer,
)


class UserSerializer(serializers.ModelSerializer):
    is_cas = serializers.SerializerMethodField("is_cas_user")
    groups = GroupSerializer(many=True)

    def is_cas_user(self, user) -> bool:
        """
        Content from calculated field "is_cas" (True if user registred through CAS, or False).
        """
        return user.is_cas_user()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "is_cas",
            "is_validated_by_admin",
            "groups",
        ]


class UserRelatedField(serializers.RelatedField):
    def display_value(self, instance):
        return instance

    def to_representation(self, value):
        return str(value)

    def to_internal_value(self, data):
        if type(data) == str:
            return User.objects.get(username=data)
        elif type(data) == int:
            return User.objects.get(pk=data)


class UserGroupsSerializer(serializers.ModelSerializer):
    groups = serializers.ListField(child=serializers.IntegerField(), required=True)
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "groups",
        ]


class AssociationUsersSerializer(serializers.ModelSerializer):
    # TODO Check drf-spectacular error.
    user = UserRelatedField(queryset=User.objects.all(), many=False)
    association = SimpleAssociationDataSerializer()

    class Meta:
        model = AssociationUsers
        fields = [
            "user",
            "has_office_status",
            "association",
        ]


class CustomRegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone")

    """
    def get_validation_exclusions(self):
        exclusions = super(CustomRegisterSerializer, self).get_validation_exclusions()
        return exclusions + ["phone"]
    """

    def validate_email(self, value):
        ModelClass = self.Meta.model
        if ModelClass.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                _("This email address is already in use.")
            )
        return value

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = request.data
        adapter.save_user(request, user, self)

        user.username = self.cleaned_data["email"]
        try:
            user.phone = self.cleaned_data["phone"]
        except KeyError:
            ...

        user.save()
        return user


class PasswordChangeSerializer(DJRestAuthPasswordChangeSerializer):
    """
    Overrided PasswordChangeSerializer to prevent CAS users to change their passwords.
    """

    def save(self):
        request = self.context.get("request")
        try:
            user = User.objects.get(email=request.user.email)
            if user.is_cas_user():
                raise exceptions.ValidationError(
                    {"detail": [_("Unable to change the password of a CAS account.")]}
                )
            else:
                self.set_password_form.save()
                if not self.logout_on_password_change:
                    from django.contrib.auth import update_session_auth_hash

                    update_session_auth_hash(self.request, self.user)
        except ObjectDoesNotExist:
            ...


class PasswordResetSerializer(DJRestAuthPasswordResetSerializer):
    """
    Overrided PasswordResetSerializer to prevent CAS users to reset their passwords.
    """

    def save(self):
        if "allauth" in settings.INSTALLED_APPS:
            from allauth.account.forms import default_token_generator
        else:
            from django.contrib.auth.tokens import default_token_generator

        request = self.context.get("request")
        # Set some values to trigger the send_email method.
        opts = {
            "use_https": request.is_secure(),
            "from_email": getattr(settings, "DEFAULT_FROM_EMAIL"),
            "request": request,
            "token_generator": default_token_generator,
        }

        opts.update(self.get_email_options())

        try:
            user = User.objects.get(email=request.data["email"])
            if user.is_cas_user():
                raise exceptions.ValidationError(
                    {"detail": [_("Unable to reset the password of a CAS account.")]}
                )
            else:
                self.reset_form.save(**opts)
        except ObjectDoesNotExist:
            ...
