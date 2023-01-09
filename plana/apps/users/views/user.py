"""
Views directly linked to users and their links with other models.
"""
from allauth.account.forms import default_token_generator
from allauth.socialaccount.models import SocialAccount
from dj_rest_auth.views import UserDetailsView as DJRestAuthUserDetailsView
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, IsAuthenticated

from plana.apps.users.models.user import User
from plana.apps.users.serializers.user import UserSerializer
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                "is_validated_by_admin",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter for members not validated by an admin",
            ),
            OpenApiParameter(
                "is_cas",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter for members logged through CAS",
            ),
        ]
    )
)
class UserListCreate(generics.ListCreateAPIView):
    """
    GET : Lists all users.

    POST : Create an account for another person as a manager.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = User.objects.filter(is_active=True).order_by("id")
        booleans = {"true": True, "false": False}
        is_validated_by_admin = self.request.query_params.get("is_validated_by_admin")
        is_cas = self.request.query_params.get("is_cas")
        if is_validated_by_admin is not None:
            queryset = queryset.filter(
                is_validated_by_admin=booleans.get(is_validated_by_admin)
            )
        # TODO Test with CAS.
        # if is_cas is not None:
        # social_accounts_queryset = SocialAccount.objects.all()
        # queryset = queryset.intersection(queryset, social_accounts_queryset)
        return queryset

    def get(self, request, *args, **kwargs):
        if request.user.is_svu_manager or request.user.is_crous_manager:
            return self.list(request, *args, **kwargs)
        return response.Response(
            {"error": _("Bad request.")},
            status=status.HTTP_403_FORBIDDEN,
        )

    def post(self, request, *args, **kwargs):
        if request.user.is_svu_manager or request.user.is_crous_manager:
            request.data.update(
                {"username": request.data["email"], "is_validated_by_admin": True}
            )
            return self.create(request, *args, **kwargs)
        return response.Response(
            {"error": _("Bad request.")},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@extend_schema(methods=["PUT"], exclude=True)
class UserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    GET : Lists a user with all details.

    PATCH : Updates a user field (with a restriction on CAS auto-generated fields).

    DELETE : Removes a user from the database (with a restriction on manager users).
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        if self.request.method == "PUT":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        if request.user.is_svu_manager or request.user.is_crous_manager:
            return self.retrieve(request, *args, **kwargs)
        return response.Response(
            {"error": _("Bad request.")},
            status=status.HTTP_403_FORBIDDEN,
        )

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        if request.user.is_svu_manager or request.user.is_crous_manager:
            try:
                user = User.objects.get(id=kwargs["pk"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("Bad request.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if user.get_cas_user():
                for restricted_field in [
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                ]:
                    request.data.pop(restricted_field, False)

            if (
                "is_validated_by_admin" in request.data
                and request.data["is_validated_by_admin"] == "true"
            ):
                current_site = get_current_site(request)
                context = {
                    "site_domain": current_site.domain,
                    "site_name": current_site.name,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "manager_email_address": request.user.email,
                    "documentation_url": settings.APP_DOCUMENTATION_URL,
                }
                if user.get_cas_user():
                    template = MailTemplate.objects.get(
                        code="MANAGER_ACCOUNT_CONFIRMATION_LDAP"
                    )
                else:
                    template = MailTemplate.objects.get(
                        code="MANAGER_ACCOUNT_CONFIRMATION"
                    )
                    # TODO New password generated through the form doesn't work.
                    context[
                        "password_reset_url"
                    ] = f"{settings.EMAIL_TEMPLATE_PASSWORD_RESET_URL}?uid={'%x' % user.id}&token={default_token_generator.make_token(user)}"
                send_mail(
                    from_=settings.DEFAULT_FROM_EMAIL,
                    to_=user.email,
                    subject=template.subject.replace(
                        "{{ site_name }}", context["site_name"]
                    ),
                    message=template.parse_vars(user, request, context),
                )
            return self.partial_update(request, *args, **kwargs)
        return response.Response(
            {"error": _("Bad request.")},
            status=status.HTTP_403_FORBIDDEN,
        )

    def delete(self, request, *args, **kwargs):
        if request.user.is_svu_manager or request.user.is_crous_manager:
            try:
                user = User.objects.get(id=kwargs["pk"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("No user found.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if (
                (user.is_superuser is True)
                or user.is_svu_manager
                or user.is_crous_manager
            ):
                return response.Response(
                    {"error": _("Cannot delete superuser.")},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if user.is_validated_by_admin == False:
                current_site = get_current_site(request)
                context = {
                    "site_domain": current_site.domain,
                    "site_name": current_site.name,
                    "manager_email_address": request.user.email,
                }
                template = MailTemplate.objects.get(code="MANAGER_ACCOUNT_REJECTION")
                send_mail(
                    from_=settings.DEFAULT_FROM_EMAIL,
                    to_=user.email,
                    subject=template.subject.replace(
                        "{{ site_name }}", context["site_name"]
                    ),
                    message=template.parse_vars(request.user, request, context),
                )

            return self.destroy(request, *args, **kwargs)
        return response.Response(
            {"error": _("Bad request.")},
            status=status.HTTP_403_FORBIDDEN,
        )


class PasswordResetConfirm(generics.GenericAPIView):
    """
    POST : Blank redirection to make the password reset work
    (see https://dj-rest-auth.readthedocs.io/en/latest/faq.html ).
    """


@extend_schema(methods=["PUT"], exclude=True)
class UserAuthView(DJRestAuthUserDetailsView):
    """
    Overrided UserDetailsView to prevent CAS users to change their own auto-generated fields.
    """

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        request.data.pop("is_validated_by_admin", False)
        if request.user.get_cas_user():
            for restricted_field in ["username", "email", "first_name", "last_name"]:
                request.data.pop(restricted_field, False)
        return self.partial_update(request, *args, **kwargs)
