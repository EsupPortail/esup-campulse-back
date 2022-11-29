from django.test import TestCase
from django.urls import reverse

from allauth.socialaccount.models import SocialAccount
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory, force_authenticate

from plana.apps.users.models.user import User
from plana.apps.users.serializers.user import (
    PasswordChangeSerializer,
    PasswordResetSerializer,
)


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

        request = APIRequestFactory().post({}, format="json")
        force_authenticate(request, user)
        request.user = user

        cls.request = request
        cls.user = user

    def test_change_password_as_local_user(self):
        """
        Raises an AttributeError because form is valid.
        """
        passwords = {"new_password1": "passedemot", "new_password2": "passedemot"}
        serializer = PasswordChangeSerializer(
            reverse("rest_password_change"),
            context={"request": self.request, "data": passwords},
        )
        serializer.validate(passwords)
        with self.assertRaises(AttributeError):
            serializer.save()


class TestLocalUserPasswordResetSerializer(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(
            username="Georges",
            email="georges@saucisse.fr",
            is_validated_by_admin=True,
        )

        request = APIRequestFactory().post({}, format="json")
        request.data = {"email": "georges@saucisse.fr"}

        cls.request = request
        cls.user = user

    def test_reset_password_as_local_user(self):
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

        request = APIRequestFactory().post({}, format="json")
        force_authenticate(request, user)
        request.user = user

        cls.request = request
        cls.user = user

    def test_change_password_as_cas_user(self):
        """
        Raises a ValidationError triggered by the custom Serializer.
        """
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

        request = APIRequestFactory().post({}, format="json")
        request.data = {"email": "georges-cas@unistra.fr"}

        cls.request = request
        cls.user = user

    def test_reset_password_as_cas_user(self):
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
