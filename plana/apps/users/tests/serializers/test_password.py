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
        request.user = user

        cls.request_data = passwords
        cls.request = request
        cls.user = user

    def test_change_password_as_cas(self):
        serializer = PasswordChangeSerializer(
            reverse("rest_password_change"),
            context={"request": self.request},
        )
        with self.assertRaises(ValidationError):
            serializer.save()
