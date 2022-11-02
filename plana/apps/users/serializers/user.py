from rest_framework import serializers

from dj_rest_auth.registration.serializers import RegisterSerializer

from .models import User
from plana.apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CustomRegisterSerializer(RegisterSerializer):
    username = None
    email = None
    password1 = None
    password2 = None
#    username, email, password1, password2 = (None,) * 4
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email_1 = serializers.CharField(required=True)
    email_2 = serializers.CharField(required=True)
    phone = serializers.CharField(required=False)
    # TODO : add multiple association name + user is president (not required), user status/role (required)

    def get_cleaned_data(self):
        data_dict = super().get_cleaned_data()
        data_dict['first_name'] = self.validated_data.get('first_name', '')
        data_dict['last_name'] = self.validated_data.get('last_name', '')
        data_dict['phone'] = self.validated_data.get('phone', '')

        if self.validated_data.get('email_1') == self.validated_data.get('email_2'):
            data_dict['username'] = self.validated_data.get('email_1')
            data_dict['email'] = self.validated_data.get('email_1')

        return data_dict

