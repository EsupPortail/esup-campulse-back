"""Views directly linked to users and their links with other models."""

from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress
from allauth.account.utils import user_pk_to_url_str
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.db.models import Exists, OuterRef, Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, generics, response, status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.contents.models.setting import Setting
from plana.apps.history.models.history import History
from plana.apps.users.models.user import AssociationUser, User
from plana.apps.users.permissions import UserUpdatePermission
from plana.apps.users.provider import CASProvider
from plana.apps.users.serializers.user import (
    UserPartialDataSerializer,
    UserSerializer,
    UserUpdateSerializer, UserCreateSerializer,
)
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail, to_bool


class UserListCreate(generics.ListCreateAPIView):
    """/users/ route."""

    filter_backends = [filters.SearchFilter]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = User.objects.all().order_by("id")
    search_fields = [
        "username__nospaces__unaccent",
        "first_name__nospaces__unaccent",
        "last_name__nospaces__unaccent",
        "email__nospaces__unaccent",
        "associations__name__nospaces__unaccent",
    ]

    def get_queryset(self):
        return (
            super().get_queryset()
            .annotate(
                has_validated_email_user_annot=Exists(EmailAddress.objects.filter(user_id=OuterRef('pk'), verified=True)),
                is_cas_user_annot=Exists(SocialAccount.objects.filter(user_id=OuterRef('pk'), provider=CASProvider.id)),
            )
            .prefetch_related('associations')
        )

    def get_serializer_class(self):
        if not self.request.user.has_perm("users.view_user_anyone") and not self.request.user.has_perm(
            "users.view_user_misc"
        ):
            self.serializer_class = UserPartialDataSerializer
        else:
            self.serializer_class = UserSerializer
        if self.request.method == "POST":
            self.serializer_class = UserCreateSerializer
        return super().get_serializer_class()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by first name and last name.",
            ),
            OpenApiParameter(
                "email",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by email.",
            ),
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
            OpenApiParameter(
                "association_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by Association ID.",
            ),
            OpenApiParameter(
                "institutions",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by Institutions IDs.",
            ),
        ],
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """List users sharing the same association, or all users (manager)."""
        name = request.query_params.get("name")
        email = request.query_params.get("email")
        is_validated_by_admin = request.query_params.get("is_validated_by_admin")
        is_cas = request.query_params.get("is_cas")
        association_id = request.query_params.get("association_id")
        institutions = request.query_params.get("institutions")

        if not request.user.has_perm("users.view_user_anyone") and not request.user.has_perm("users.view_user_misc"):
            self.queryset = self.queryset.filter(associations__in=request.user.get_user_associations())
        else:
            if name is not None and name != "":
                name = str(name).strip()
                self.queryset = self.queryset.filter(
                    Q(first_name__nospaces__unaccent__icontains=name.replace(" ", ""))
                    | Q(last_name__nospaces__unaccent__icontains=name.replace(" ", ""))
                )

            if email is not None and email != "":
                email = str(email).strip()
                self.queryset = self.queryset.filter(email__nospaces__unaccent__icontains=email.replace(" ", ""))

            if is_validated_by_admin is not None and is_validated_by_admin != "":
                is_validated_by_admin = to_bool(is_validated_by_admin)
                email_validated_user_ids = EmailAddress.objects.filter(verified=True).values_list("user_id")
                self.queryset = self.queryset.filter(
                    is_validated_by_admin=is_validated_by_admin,
                    id__in=email_validated_user_ids,
                )

            if is_cas is not None and is_cas != "":
                is_cas = to_bool(is_cas)
                cas_ids_list = SocialAccount.objects.filter(provider='cas').values_list("user_id")
                self.queryset = (
                    self.queryset.filter(id__in=cas_ids_list) if is_cas else self.queryset.exclude(id__in=cas_ids_list)
                )

            if association_id is not None and association_id != "":
                assos_users_query = AssociationUser.objects.filter(association_id=association_id).values_list(
                    "user_id"
                )
                self.queryset = self.queryset.filter(id__in=assos_users_query)

            if institutions is not None:
                misc_users_query = User.objects.filter(
                    groupinstitutionfunduser__institution__isnull=True,
                    groupinstitutionfunduser__fund__isnull=True,
                    associations__isnull=True,
                )
                commission_users_query = User.objects.filter(groupinstitutionfunduser__fund__isnull=False)
                if institutions == "":
                    self.queryset = self.queryset.filter(
                        Q(id__in=misc_users_query.values_list("id"))
                        | Q(id__in=commission_users_query.values_list("id"))
                    )
                else:
                    institutions_ids = institutions.split(",")
                    check_other_users = False
                    if "" in institutions_ids:
                        check_other_users = True
                    institutions_ids = [
                        institution_id
                        for institution_id in institutions_ids
                        if institution_id != "" and institution_id.isdigit()
                    ]

                    associations_ids = Association.objects.filter(institution_id__in=institutions_ids).values_list(
                        "id"
                    )
                    assos_users_query = AssociationUser.objects.filter(association_id__in=associations_ids)
                    commission_users_query = User.objects.filter(groupinstitutionfunduser__fund__institution_id__in=institutions_ids)
                    institution_users_query = User.objects.filter(groupinstitutionfunduser__institution_id__in=institutions_ids)

                    if check_other_users:
                        self.queryset = self.queryset.filter(
                            Q(id__in=assos_users_query.values_list("user_id"))
                            | Q(id__in=misc_users_query.values_list("id"))
                            | Q(id__in=commission_users_query.values_list("id"))
                            | Q(id__in=institution_users_query.values_list("id"))
                        )
                    else:
                        self.queryset = self.queryset.filter(
                            Q(id__in=assos_users_query.values_list("user_id"))
                            | Q(id__in=commission_users_query.values_list("id"))
                            | Q(id__in=institution_users_query.values_list("id"))
                        )

        return self.list(request, *args, **kwargs)

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

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = UserSerializer
        else:
            self.serializer_class = UserUpdateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        if self.request.method != "GET":
            self.permission_classes.append(UserUpdatePermission)
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        """Retrieve a user with all details."""

        if not request.user.has_perm("users.view_user_anyone") and not self.request.user.has_perm(
            "users.view_user_misc"
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this user.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        return self.retrieve(request, *args, **kwargs)

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
                uid = user_pk_to_url_str(user)
                token = default_token_generator.make_token(user)
                context["password_reset_url"] = (
                    f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_PASSWORD_RESET_PATH}"
                    f"?uid={uid}&token={token}"
                )
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
