from allauth.socialaccount.models import SocialAccount
from rest_framework import serializers
from plana.apps.users.models import User
from plana.apps.users.provider import CASProvider

class UserSerializer(serializers.ModelSerializer):
    is_cas = serializers.SerializerMethodField('is_cas_user')

    def is_cas_user(self, user) -> bool:
        try:
            account: SocialAccount = user.socialaccount_set.get(provider=CASProvider.id)
            return True
        except SocialAccount.DoesNotExist:
            return False

    class Meta:
        model = User
        fields = ['id', 'is_cas', 'username', 'first_name', 'last_name', 'email', 'phone', 'groups', 'association_members']
