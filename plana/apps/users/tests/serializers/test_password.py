from django.test import TestCase
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate
from allauth.socialaccount.models import SocialAccount

from plana.apps.users.models.user import User
from plana.apps.users.serializers.user import PasswordChangeSerializer


class TestLocalUserPasswordChangeSerializer(TestCase):
    """
    Testing password methods for a non-CAS user.
    """
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="Georges",
            email="georges@saucisse.fr",
            is_validated_by_admin=True,
        )
        passwords = {
            "new_password1": "passedemot",
            "new_password2": "passedemot",
        }
        request = APIRequestFactory().post(passwords, format="json")
        force_authenticate(request, user)
        request.user = user

        cls.request_data = passwords
        cls.request = request
        cls.user = user

    def test_change_password_as_local_user(self):
        """
        Raises an AttributeError because form is valid.
        """
        serializer = PasswordChangeSerializer(
            reverse("rest_password_change"),
            context={"request": self.request},
        )
        serializer.validate(self.request_data)
        with self.assertRaises(AttributeError):
            serializer.save()


class TestCASUserPasswordChangeSerializer(TestCase):
    """
    Testing password methods for a CAS user.
    """
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
            "new_password1": "passedemot",
            "new_password2": "passedemot",
        }
        request = APIRequestFactory().post(passwords, format="json")
        force_authenticate(request, user)
        request.user = user

        cls.request_data = passwords
        cls.request = request
        cls.user = user

    def test_change_password_as_cas_user(self):
        """
        Raises a ValidationError triggered by the custom Serializer.
        """
        serializer = PasswordChangeSerializer(
            reverse("rest_password_change"),
            context={"request": self.request},
        )
        with self.assertRaises(ValidationError):
            serializer.save()
