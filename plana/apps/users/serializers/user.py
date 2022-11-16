from rest_framework import serializers

from allauth.account.adapter import get_adapter

from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _

from plana.apps.users.models.user import User, AssociationUsers


class UserSerializer(serializers.ModelSerializer):
    is_cas = serializers.SerializerMethodField("is_cas_user")

    def is_cas_user(self, user) -> bool:
        """
        Contenu du champ calculé "is_cas" (True si l'utilisateur s'est inscrit via CAS, False sinon).
        """
        return user.is_cas_user()

    class Meta:
        model = User
        fields = [
            "id",
            "is_cas",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "groups",
            "association_members",
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


class AssociationUsersSerializer(serializers.ModelSerializer):
    # TODO Check drf-spectacular error.
    user = UserRelatedField(queryset=User.objects.all(), many=False)

    class Meta:
        model = AssociationUsers
        fields = "__all__"


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = (
            "id",
            "name",
        )


class CustomRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone")

    def get_validation_exclusions(self):
        exclusions = super(CustomRegisterSerializer, self).get_validation_exclusions()
        return exclusions + ["phone"]

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
        user.phone = self.cleaned_data["phone"]

        user.save()
        return user
