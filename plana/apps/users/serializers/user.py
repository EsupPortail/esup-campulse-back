from rest_framework import serializers
from plana.apps.users.models import User

class UserSerializer(serializers.ModelSerializer):
    is_cas = serializers.SerializerMethodField('is_cas_user')

    def is_cas_user(self, user):
        return user.is_cas_user()
        
    class Meta:
        model = User
        fields = ['id', 'is_cas', 'username', 'first_name', 'last_name', 'email', 'phone', 'groups', 'association_members']
