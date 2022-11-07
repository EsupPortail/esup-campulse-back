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


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    password2 = None
    email_2 = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phone = serializers.CharField(required=False)
    role = serializers.CharField(required=True)
    password1 = serializers.CharField(required=False, default="")
    # TODO : add user is cas (required, boolean)
    # TODO : add checks on User and AssociationUsers objects creation
    # TODO : use Model User instead of fields

    def validate_password1(self, password):
        char_list = string.ascii_letters + string.digits + string.punctuation
        result = []
        for i in range(8):
            result.append(random.choice(char_list))
        return "".join(result)

    def validate(self, data):
        data['password2'] = data['password1']
        return data

    def get_cleaned_data(self):
        data_dict = super().get_cleaned_data()

        data_dict['first_name'] = self.validated_data.get('first_name', '')
        data_dict['last_name'] = self.validated_data.get('last_name', '')
        data_dict['phone'] = self.validated_data.get('phone', '')
        data_dict['role'] = self.validated_data.get('role', '')

        if self.validated_data.get('email') == self.validated_data.get('email_2'):
            data_dict['username'] = self.validated_data.get('email')
        else:
            raise Exception('Les deux adresses mail doivent être identiques.')

        return data_dict

