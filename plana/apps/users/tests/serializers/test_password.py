"""List of tests done on password serializers."""

from allauth.socialaccount.models import SocialAccount
from django.test import TestCase
from django.urls import reverse
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate

from plana.apps.users.models.user import User
from plana.apps.users.serializers.user_auth import (
    PasswordChangeSerializer,
    PasswordResetSerializer,
)


class TestLocalUserPasswordChangeSerializer(TestCase):
    """Testing password change for an authenticated non-CAS user."""

    @classmethod
    def setUpTestData(cls):
        """Defalut data to test password change."""
        user = User.objects.create_user(
            username="JohnDoe",
            email="john@doe.fr",
            is_validated_by_admin=True,
        )

        request = APIRequestFactory().post({}, format="json")
        force_authenticate(request, user)
        request.user = user

        cls.request = request
        cls.user = user

    def test_change_password_as_local_user(self):
        """Raises an AttributeError because form is valid."""
        passwords = {"new_password1": "passedemot", "new_password2": "passedemot"}
        serializer = PasswordChangeSerializer(
            reverse("rest_password_change"),
            context={"request": self.request, "data": passwords},
        )
        serializer.validate(passwords)
        with self.assertRaises(AttributeError):
            serializer.save()


class TestLocalUserPasswordResetSerializer(TestCase):
    """Testing password reset for a non-authenticated non-CAS user."""

    @classmethod
    def setUpTestData(cls):
        """Defalut data to test password reset."""
        user = User.objects.create_user(
            username="JohnDoe",
            email="john@doe.fr",
            is_validated_by_admin=True,
        )

        request = APIRequestFactory().post({}, format="json")
        request.data = {"email": "john@doe.fr"}

        cls.request = request
        cls.user = user

    def test_reset_password_as_local_user(self):
        """Raises an AttributeError because form is valid."""
        passwords = {
            "new_password1": "passedemot",
            "new_password2": "passedemot",
            "uid": hex(self.user.id),
            "token": "0123456789abcdef",
        }
        serializer = PasswordResetSerializer(
            reverse("rest_password_reset_confirm"),
            context={"request": self.request, "data": passwords},
        )
        serializer.validate(passwords)
        with self.assertRaises(AttributeError):
            serializer.save()


class TestCASUserPasswordChangeSerializer(TestCase):
    """Testing password change for an authenticated CAS user."""

    @classmethod
    def setUpTestData(cls):
        """Defalut data to test password change with CAS."""
        user = User.objects.create_user(
            username="PatriciaCAS",
            email="patricia-cas@unistra.fr",
            is_validated_by_admin=True,
        )
        SocialAccount.objects.create(provider="cas", uid="PatriciaCAS", user_id=user.id)

        request = APIRequestFactory().post({}, format="json")
        force_authenticate(request, user)
        request.user = user

        cls.request = request
        cls.user = user

    def test_change_password_as_cas_user(self):
        """Raises a ValidationError triggered by the custom Serializer."""
        passwords = {
            "new_password1": "passedemot",
            "new_password2": "passedemot",
        }
        serializer = PasswordChangeSerializer(
            reverse("rest_password_change"),
            context={"request": self.request, "data": passwords},
        )
        with self.assertRaises(ValidationError):
            serializer.save()


class TestCASUserPasswordResetSerializer(TestCase):
    """Testing password reset for a non-authenticated CAS user."""

    @classmethod
    def setUpTestData(cls):
        """Defalut data to test password reset with CAS."""
        user = User.objects.create_user(
            username="GeorgeLuCAS",
            email="george-lucas@unistra.fr",
            is_validated_by_admin=True,
        )
        SocialAccount.objects.create(provider="cas", uid="GeorgeLuCAS", user_id=user.id)

        request = APIRequestFactory().post({}, format="json")
        request.data = {"email": "george-lucas@unistra.fr"}

        cls.request = request
        cls.user = user

    def test_reset_password_as_cas_user(self):
        """Raises a ValidationError triggered by the custom Serializer."""
        passwords = {
            "new_password1": "passedemot",
            "new_password2": "passedemot",
            "uid": hex(self.user.id),
            "token": "0123456789abcdef",
        }
        serializer = PasswordResetSerializer(
            reverse("rest_password_reset_confirm"),
            context={"request": self.request, "data": passwords},
        )
        with self.assertRaises(ValidationError):
            serializer.save()
