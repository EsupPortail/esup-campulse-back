from django.test import TestCase
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate
from allauth.socialaccount.models import SocialAccount

from plana.apps.users.models.user import User
from plana.apps.users.serializers.user import PasswordChangeSerializer


class TestCASPasswordChangeSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="GeorgesCAS",
            email="georges-cas@unistra.fr",
            is_validated_by_admin=True,
        )
        social_account = SocialAccount.objects.create(
            provider="cas", uid="GeorgesCAS", user_id=user.id
        )
        passwords = {
            "old_password": "motdepasse",
            "new_password1": "passedemot",
            "new_password2": "passedemot",
        }
        request = APIRequestFactory().post(passwords, format="json")
        force_authenticate(request, user)

        cls.request_data = passwords
        cls.request = request
        cls.user = user

    def test_change_password_as_cas(self):
        """
        # Test custom validation success
        PasswordChangeSerializer.custom_validation = MagicMock(return_value=True)
        serializer = PasswordChangeSerializer(
            reverse("rest_password_change"),
            data=self.request_data
        )
        serializer.validate(self.request_data)
        PasswordChangeSerializer.custom_validation.assert_called_once_with(self.request_data)
        """

        """
        # Test custom validation error
        PasswordChangeSerializer.custom_validation = MagicMock(
            side_effect=ValidationError("failed")
        )
        serializer = PasswordChangeSerializer(
            reverse("rest_password_change"),
            data=self.request_data
        )
        with self.assertRaisesMessage(ValidationError, "failed"):
            serializer.validate(self.request_data)
        """

        print(self.user.is_cas_user())
        serializer = PasswordChangeSerializer(reverse("rest_password_change"), data=self.request_data)
        serializer.save()
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
