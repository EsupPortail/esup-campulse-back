import string, random

from rest_framework import serializers

from dj_rest_auth.registration.serializers import RegisterSerializer
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


#class CustomRegisterSerializer(serializers.Serializer):
#    first_name = serializers.CharField(required=True)
#    last_name = serializers.CharField(required=True)
#    email = serializers.CharField(required=True)
#    email_2 = serializers.CharField(required=True)
#    phone = serializers.CharField(required=False)
#    # TODO : add multiple association name + user is president (not required), user status/role (required)
#
#    def get_cleaned_data(self):
#        data_dict = {}
#        data_dict['first_name'] = self.validated_data.get('first_name', '')
#        data_dict['last_name'] = self.validated_data.get('last_name', '')
#        data_dict['phone'] = self.validated_data.get('phone', '')
#
#        if self.validated_data.get('email') == self.validated_data.get('email_2'):
#            data_dict['username'] = self.validated_data.get('email')
#            data_dict['email'] = self.validated_data.get('email')
#        else:
#            raise Exception('Les deux adresses mail doivent être identiques.')
#
#        return data_dict
#
#    def save(self, request):
#        cleaned_data = self.get_cleaned_data()
#        user = User.objects.create(**cleaned_data)
#        return user


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

