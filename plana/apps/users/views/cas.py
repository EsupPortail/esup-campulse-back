"""Special views dedicated to CAS login and operations."""

import requests
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LogoutView
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, generics, permissions

from plana.apps.history.models import History
from plana.apps.users.adapter import CASAdapter
from plana.apps.users.models import User
from plana.apps.users.serializers.cas import CASSerializer
from plana.apps.users.serializers.user import CustomCASDataRegisterSerializer
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class CASLogin(SocialLoginView):
    """
    /users/auth/cas/login/ route.

    POST : Authenticates a user through CAS with django-allauth-cas and dj-rest-auth.
    """

    adapter_class = CASAdapter
    serializer_class = CASSerializer


class CASLogout(LogoutView):
    """
    /users/auth/cas/logout/ route.

    GET : Logs out a user authenticated with CAS out.

    POST : Logs out a user authenticated with CAS out.
    """

    adapter_class = CASAdapter
    serializer_class = CASSerializer

    # The user should be redirected to CASClient.get_logout_url(redirect_url=redirect_url)


# login = CASLoginView.adapter_view(CASAdapter)
# callback = CASCallbackView.adapter_view(CASAdapter)


def cas_test(request):  # pragma: no cover
    """Debug function to test the CAS server."""
    service_url = reverse("cas_verify")
    service_url = urlencode({"service": request.build_absolute_uri(service_url)})
    redirect_url = f"{settings.CAS_SERVER}login?{service_url}"
    return HttpResponseRedirect(redirect_to=redirect_url)


def cas_verify(request):  # pragma: no cover
    """Debug function to test the ticket."""
    service_url = request.build_absolute_uri(reverse("cas_verify"))
    ticket = request.GET.get("ticket")

    response = requests.post(
        request.build_absolute_uri(reverse("rest_cas_login")),
        json={
            "service": service_url,
            "ticket": ticket,
        },
        headers={
            "Accept": "application/json",
        },
    )
    if response.ok:
        return JsonResponse(response.json())
    print(response)
    return JsonResponse({})


class CASDataRegisterView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomCASDataRegisterSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch"]

    def get_object(self):
        user = self.request.user
        if user.is_validated_by_admin or not user.is_cas_user:
            raise exceptions.PermissionDenied(
                detail=_("Cannot update registration data for an already validated account or a local account.")
            )
        return user

    @transaction.atomic
    def perform_update(self, serializer):
        serializer.save()

        # Send manager notification email when data submitted
        current_site = get_current_site(self.request)
        context = {"site_domain": f"https://{current_site.domain}", "site_name": current_site.name, "account_url": (
            f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_ACCOUNT_VALIDATE_PATH}{self.request.user.pk}"
        )}
        History.objects.create(action_title="USER_REGISTERED", action_user_id=self.request.user.pk)
        template = MailTemplate.objects.get(code="MANAGER_ACCOUNT_LDAP_CREATION")
        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=self.request.user.get_user_default_manager_emails(),
            subject=template.subject.replace("{{ site_name }}", context["site_name"]),
            message=template.parse_vars(self.request.user, self.request, context),
        )
