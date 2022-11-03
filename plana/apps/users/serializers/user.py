from rest_framework import serializers

from dj_rest_auth.registration.serializers import RegisterSerializer

from plana.apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class CustomRegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    email_2 = serializers.CharField(required=True)
    phone = serializers.CharField(required=False)
    # TODO : add multiple association name + user is president (not required), user status/role (required)

    def get_cleaned_data(self):
        data_dict = {}
        data_dict['first_name'] = self.validated_data.get('first_name', '')
        data_dict['last_name'] = self.validated_data.get('last_name', '')
        data_dict['phone'] = self.validated_data.get('phone', '')

        if self.validated_data.get('email') == self.validated_data.get('email_2'):
            data_dict['username'] = self.validated_data.get('email')
            data_dict['email'] = self.validated_data.get('email')
        else:
            raise Exception('Les deux adresses mail doivent être identiques.')

        return data_dict

    def save(self, request):
        cleaned_data = self.get_cleaned_data()
        user = User.objects.create(**cleaned_data)
        return user
