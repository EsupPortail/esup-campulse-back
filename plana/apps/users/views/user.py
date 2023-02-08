"""
Views directly linked to users and their links with other models.
"""

from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress
from allauth.account.utils import user_pk_to_url_str
from allauth.socialaccount.models import SocialAccount
from dj_rest_auth.registration.views import VerifyEmailView as DJRestAuthVerifyEmailView
from dj_rest_auth.views import UserDetailsView as DJRestAuthUserDetailsView
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.users.models.user import AssociationUsers, GroupInstitutionUsers, User
from plana.apps.users.serializers.user import UserSerializer
from plana.apps.users.serializers.user_groups_institutions import (
    UserGroupsInstitutionsSerializer,
)
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail, to_bool


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
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_queryset(self):
        queryset = User.objects.filter(is_active=True).order_by("id")
        is_validated_by_admin = self.request.query_params.get("is_validated_by_admin")
        is_cas = self.request.query_params.get("is_cas")

        if is_validated_by_admin is not None and is_validated_by_admin != "":
            is_validated_by_admin = to_bool(is_validated_by_admin)
            queryset = queryset.filter(is_validated_by_admin=is_validated_by_admin)

        if is_cas is not None and is_cas != "":
            is_cas = to_bool(is_cas)
            cas_ids_list = SocialAccount.objects.filter(provider='cas').values_list(
                'user_id', flat=True
            )
            queryset = (
                queryset.filter(id__in=cas_ids_list)
                if is_cas
                else queryset.exclude(id__in=cas_ids_list)
            )

        return queryset

    def get(self, request, *args, **kwargs):
        if request.user.has_perm("users.view_user"):
            return self.list(request, *args, **kwargs)
        return response.Response(
            {"error": _("Bad request.")},
            status=status.HTTP_403_FORBIDDEN,
        )

    def post(self, request, *args, **kwargs):
        request.data.update(
            {"username": request.data["email"], "is_validated_by_admin": True}
        )
        user_response = self.create(request, *args, **kwargs)

        user = User.objects.get(id=user_response.data["id"])
        password = User.objects.make_random_password()
        user.set_password(password)
        user.save(update_fields=['password'])
        EmailAddress.objects.create(
            email=user.email, verified=True, primary=True, user_id=user.id
        )

        current_site = get_current_site(request)
        context = {
            "site_domain": current_site.domain,
            "site_name": current_site.name,
            "username": request.data["email"],
            "first_name": request.data["first_name"],
            "last_name": request.data["last_name"],
            "manager_email_address": request.data["email"],
            "documentation_url": settings.APP_DOCUMENTATION_URL,
            "password": password,
            "password_change_url": settings.EMAIL_TEMPLATE_PASSWORD_CHANGE_URL,
        }
        template = MailTemplate.objects.get(
            code="ACCOUNT_CREATED_BY_MANAGER_CONFIRMATION"
        )
        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=request.data["email"],
            subject=template.subject.replace("{{ site_name }}", context["site_name"]),
            message=template.parse_vars(request.user, request, context),
        )

        return user_response


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
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        if request.user.has_perm("users.view_user"):
            return self.retrieve(request, *args, **kwargs)
        return response.Response(
            {"error": _("Bad request.")},
            status=status.HTTP_403_FORBIDDEN,
        )

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_superuser is True or user.is_staff is True:
            return response.Response(
                {"error": _("Cannot edit superuser.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if user.is_cas_user():
            for restricted_field in [
                "username",
                "email",
                "first_name",
                "last_name",
            ]:
                request.data.pop(restricted_field, False)

        if (
            "is_validated_by_admin" in request.data
            and to_bool(request.data["is_validated_by_admin"]) is True
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
            if user.is_cas_user():
                template = MailTemplate.objects.get(
                    code="MANAGER_ACCOUNT_CONFIRMATION_LDAP"
                )
            else:
                template = MailTemplate.objects.get(code="MANAGER_ACCOUNT_CONFIRMATION")
                uid = user_pk_to_url_str(user)
                token = default_token_generator.make_token(user)
                context[
                    "password_reset_url"
                ] = f"{settings.EMAIL_TEMPLATE_PASSWORD_RESET_URL}?uid={uid}&token={token}"
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=user.email,
                subject=template.subject.replace(
                    "{{ site_name }}", context["site_name"]
                ),
                message=template.parse_vars(user, request, context),
            )
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("No user found.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_superuser is True or user.is_staff is True:
            return response.Response(
                {"error": _("Cannot delete superuser.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        current_site = get_current_site(request)
        if user.is_validated_by_admin is False:
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
        else:
            context = {
                "site_domain": current_site.domain,
                "site_name": current_site.name,
            }
            template = MailTemplate.objects.get(code="ACCOUNT_DELETE")
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=user.email,
                subject=template.subject.replace(
                    "{{ site_name }}", context["site_name"]
                ),
                message=template.parse_vars(request.user, request, context),
            )

        return self.destroy(request, *args, **kwargs)


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
        if "is_validated_by_admin" in request.data:
            request.data.pop("is_validated_by_admin", False)
        if request.user.is_cas_user():
            for restricted_field in ["username", "email", "first_name", "last_name"]:
                if restricted_field in request.data:
                    request.data.pop(restricted_field, False)

            if request.user.is_validated_by_admin is False:
                current_site = get_current_site(request)
                user_id = request.user.id
                context = {
                    "site_domain": current_site.domain,
                    "site_name": current_site.name,
                    "account_url": f"{settings.EMAIL_TEMPLATE_ACCOUNT_VALIDATE_URL}{user_id}",
                }
                template = MailTemplate.objects.get(
                    code="GENERAL_MANAGER_LDAP_ACCOUNT_CONFIRMATION"
                )
                # manager = User.objects.filter(groups__name="Gestionnaire SVU").first()
                send_mail(
                    from_=settings.DEFAULT_FROM_EMAIL,
                    to_=settings.DEFAULT_MANAGER_GENERAL_EMAIL,
                    subject=template.subject.replace(
                        "{{ site_name }}", context["site_name"]
                    ),
                    message=template.parse_vars(request.user, request, context),
                )

        return self.partial_update(request, *args, **kwargs)


class UserAuthVerifyEmailView(DJRestAuthVerifyEmailView):
    """
    Overrided VerifyEmailView to send an email to a manager.
    """

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.kwargs['key'] = serializer.validated_data['key']
        confirmation = self.get_object()
        confirmation.confirm(self.request)

        user = User.objects.get(email=confirmation.email_address)
        associations_ids = AssociationUsers.objects.filter(user_id=user.id).values_list(
            'association_id', flat=True
        )
        associations_site = Association.objects.filter(
            id__in=associations_ids, is_site=True
        )

        current_site = get_current_site(request)
        context = {
            "site_domain": current_site.domain,
            "site_name": current_site.name,
            "account_url": f"{settings.EMAIL_TEMPLATE_ACCOUNT_VALIDATE_URL}{user.id}",
        }
        if associations_site.count() > 0:
            template = MailTemplate.objects.get(
                code="GENERAL_MANAGER_LOCAL_ACCOUNT_CONFIRMATION"
            )
            # email = User.objects.filter(groups__name="Gestionnaire SVU").first().email
            email = settings.DEFAULT_MANAGER_GENERAL_EMAIL
        else:
            template = MailTemplate.objects.get(
                code="MISC_MANAGER_LOCAL_ACCOUNT_CONFIRMATION"
            )
            # email = User.objects.filter(groups__name="Gestionnaire Crous").first().email
            email = settings.DEFAULT_MANAGER_MISC_EMAIL
        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=email,
            subject=template.subject.replace("{{ site_name }}", context["site_name"]),
            message=template.parse_vars(user, request, context),
        )

        return response.Response({'detail': _('ok')}, status=status.HTTP_200_OK)
