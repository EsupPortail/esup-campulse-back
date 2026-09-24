"""Views directly linked to users and their links with other models."""

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.db.models import Exists, OuterRef
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, response
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.contents.models.setting import Setting
from plana.apps.history.models.history import History
from plana.apps.users.filters import UserFilter
from plana.apps.users.models.user import AssociationUser, User
from plana.apps.users.permissions import UserManagerUpdatePermission
from plana.apps.users.provider import CASProvider
from plana.apps.users.serializers.user import (
    UserPartialDataSerializer,
    UserSerializer,
    UserUpdateSerializer, UserCreateSerializer,
)
from plana.apps.users.utils import build_password_reset_url
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class UserListCreate(generics.ListCreateAPIView):
    """/users/ route."""

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    filterset_class = UserFilter
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    http_method_names = ["get", "post"]
    queryset = User.objects.all().order_by("id")
    search_fields = [
        "username__nospaces__unaccent",
        "first_name__nospaces__unaccent",
        "last_name__nospaces__unaccent",
        "email__nospaces__unaccent",
        "associations__name__nospaces__unaccent",
    ]

    def get_queryset(self):
        """List users sharing the same association, or all users (manager)."""
        base_queryset = (
            super().get_queryset()
            .annotate(
                has_validated_email_user_annot=Exists(EmailAddress.objects.filter(user_id=OuterRef('pk'), verified=True)),
                is_cas_user_annot=Exists(SocialAccount.objects.filter(user_id=OuterRef('pk'), provider=CASProvider.id)),
            )
            .prefetch_related('associations')
        )
        if self.request.user.is_staff:
            return base_queryset.managed_users(self.request.user)
        else:
            return base_queryset.filter(
                associations__in=self.request.user.get_user_associations(),
                is_validated_by_admin=True
            )

    def get_serializer_class(self):
        if not self.request.user.is_staff:
            self.serializer_class = UserPartialDataSerializer
        else:
            self.serializer_class = UserSerializer
        if self.request.method == "POST":
            self.serializer_class = UserCreateSerializer
        return super().get_serializer_class()

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    /users/{id} route.
    For managers only
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ["get", "patch", "delete"]
    permission_classes = [IsAuthenticated, DjangoModelPermissions, UserManagerUpdatePermission]

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = UserSerializer
        else:
            self.serializer_class = UserUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return super().get_queryset().managed_users(self.request.user)

    def update(self, request, *args, **kwargs):
        """Update a user field (with a restriction on CAS auto-generated fields)."""

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        self._handle_user_update_emails(user, serializer.validated_data, request)

        return response.Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        """Destroys a user from the database (with a restriction on manager users)."""
        user = self.get_object()

        current_site = get_current_site(request)
        context = {
            "site_domain": current_site.domain,
            "site_name": current_site.name,
        }
        if not user.is_validated_by_admin:
            context["manager_email_address"] = request.user.email
            template_code = "USER_ACCOUNT_REJECTION"
        else:
            template_code = "USER_ACCOUNT_DELETION"

        self._send_template_mail(template_code, user.email, request.user, request, context)

        return self.destroy(request, *args, **kwargs)

    def _send_template_mail(self, template_code, to, user, request, context):
        template = MailTemplate.objects.get(code=template_code)
        subject = template.subject.replace("{{ site_name }}", context["site_name"])
        message = template.parse_vars(user, request, context)
        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=to,
            subject=subject,
            message=message
        )

    def _handle_user_update_emails(self, user, validated_data, request):
        current_site = get_current_site(request)
        base_context = {
            "site_domain": current_site.domain,
            "site_name": current_site.name,
            "manager_email_address": request.user.email,
        }

        if "can_submit_projects" in validated_data:
            template_code = (
                "USER_OR_ASSOCIATION_PROJECT_SUBMISSION_ENABLED"
                if validated_data["can_submit_projects"]
                else "USER_OR_ASSOCIATION_PROJECT_SUBMISSION_DISABLED"
            )
            self._send_template_mail(template_code, user.email, request.user, request, base_context)

        if validated_data.get("is_validated_by_admin"):
            context = {**base_context,
                       "username": user.username,
                       "first_name": user.first_name,
                       "last_name": user.last_name,
                       "documentation_url": Setting.get_setting("APP_DOCUMENTATION_URL")}
            if user.is_cas_user:
                template_code = "USER_ACCOUNT_LDAP_CONFIRMATION"
            else:
                template_code = "USER_ACCOUNT_CONFIRMATION"
                context["password_reset_url"] = build_password_reset_url(user)
            History.objects.create(
                action_title="USER_VALIDATED",
                action_user=request.user,
                user=user
            )
            self._send_template_mail(template_code, user.email, user, request, context)

            context["user_association_url"] = (
                f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_USER_ASSOCIATION_VALIDATE_PATH}"
            )
            unvalidated_assos_user = (
                AssociationUser.objects
                .filter(user=user, is_validated_by_admin=False)
                .select_related("association__institution")
            )
            for assoc_user in unvalidated_assos_user:
                managers = assoc_user.association.institution.default_institution_managers()
                manager_emails = list(managers.values_list("email", flat=True))
                self._send_template_mail("MANAGER_ACCOUNT_ASSOCIATION_USER_CREATION", manager_emails, request.user, request, context)
