import string, random

from rest_framework import serializers

from allauth.account.adapter import get_adapter

from django.contrib.auth.models import Group

from plana.apps.users.models import User, AssociationUsers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class AssociationUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssociationUsers
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name',)


class CustomRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone')

    # TODO: Add check if user exists before save
    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = request.data
        adapter.save_user(request, user, self)

        user.username = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']

        user.save()
        return user

