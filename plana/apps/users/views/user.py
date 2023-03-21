"""Views directly linked to users and their links with other models."""

import datetime

from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress
from allauth.account.utils import user_pk_to_url_str
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.users.models.user import (
    AssociationUsers,
    GroupInstitutionCommissionUsers,
    User,
)
from plana.apps.users.provider import CASProvider
from plana.apps.users.serializers.user import UserPartialDataSerializer, UserSerializer
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
        ]
    )
)
class UserListCreate(generics.ListCreateAPIView):
    """
    GET : Lists all users for manager, or users sharing the same association.

    POST : Create an account for another person as a manager.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, DjangoModelPermissions]

    def get_serializer_class(self):
        if not self.request.user.has_perm(
            "users.view_user_anyone"
        ) and not self.request.user.has_perm("users.view_user_misc"):
            self.serializer_class = UserPartialDataSerializer
        else:
            self.serializer_class = UserSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = User.objects.all().order_by("id")
        is_validated_by_admin = self.request.query_params.get("is_validated_by_admin")
        is_cas = self.request.query_params.get("is_cas")
        association_id = self.request.query_params.get("association_id")
        institutions = self.request.query_params.get("institutions")

        if not self.request.user.has_perm(
            "users.view_user_anyone"
        ) and not self.request.user.has_perm("users.view_user_misc"):
            queryset = queryset.filter(
                id__in=AssociationUsers.objects.filter(
                    association_id__in=self.request.user.get_user_associations().values_list(
                        "id"
                    )
                ).values_list("user_id")
            )
        else:
            if is_validated_by_admin is not None and is_validated_by_admin != "":
                is_validated_by_admin = to_bool(is_validated_by_admin)
                email_validated_user_ids = EmailAddress.objects.filter(
                    verified=True
                ).values_list("user_id", flat=True)
                queryset = queryset.filter(
                    is_validated_by_admin=is_validated_by_admin,
                    id__in=email_validated_user_ids,
                )

            if is_cas is not None and is_cas != "":
                is_cas = to_bool(is_cas)
                cas_ids_list = SocialAccount.objects.filter(provider='cas').values_list(
                    "user_id", flat=True
                )
                queryset = (
                    queryset.filter(id__in=cas_ids_list)
                    if is_cas
                    else queryset.exclude(id__in=cas_ids_list)
                )

            if association_id is not None and association_id != "":
                assos_users_query = AssociationUsers.objects.filter(
                    association_id=association_id
                ).values_list("user_id", flat=True)
                queryset = queryset.filter(id__in=assos_users_query)

            if institutions is not None:
                # TODO Update the query when new permissions linked to projects will be available (need to get misc students also in associations).
                misc_users_query = User.objects.exclude(
                    id__in=AssociationUsers.objects.all().values_list(
                        "user_id", flat=True
                    )
                ).values_list("id", flat=True)
                commission_users_query = User.objects.filter(
                    id__in=GroupInstitutionCommissionUsers.objects.filter(
                        commission_id__isnull=False
                    ).values_list("user_id", flat=True)
                ).values_list("id", flat=True)
                if institutions == "":
                    queryset = queryset.filter(
                        models.Q(id__in=misc_users_query)
                        | models.Q(id__in=commission_users_query)
                    )
                else:
                    institutions_ids = institutions.split(",")
                    check_other_users = False
                    if "" in institutions_ids:
                        check_other_users = True
                        del institutions_ids[institutions_ids.index("")]

                    associations_ids = Association.objects.filter(
                        institution_id__in=institutions_ids
                    ).values_list("id", flat=True)
                    assos_users_query = AssociationUsers.objects.filter(
                        association_id__in=associations_ids
                    ).values_list("user_id", flat=True)

                    if check_other_users is True:
                        queryset = queryset.filter(
                            models.Q(id__in=assos_users_query)
                            | models.Q(id__in=misc_users_query)
                            | models.Q(id__in=commission_users_query)
                        )
                    else:
                        queryset = queryset.filter(id__in=assos_users_query)

        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        is_cas = True
        if not "is_cas" in request.data or (
            "is_cas" in request.data and request.data["is_cas"] is False
        ):
            is_cas = False
            if request.data["email"].split('@')[1] in settings.RESTRICTED_DOMAINS:
                return response.Response(
                    {
                        "error": _(
                            "This email address cannot be used for a local account."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request.data.update({"username": request.data["email"]})

        request.data.update({"is_validated_by_admin": True})
        user_response = self.create(request, *args, **kwargs)
        user = User.objects.get(id=user_response.data["id"])
        EmailAddress.objects.create(
            email=user.email, verified=True, primary=True, user_id=user.id
        )

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

        template = None
        if not is_cas:
            password = User.objects.make_random_password()
            user.set_password(password)
            user.password_last_change_date = datetime.datetime.today()
            user.save(update_fields=["password", "password_last_change_date"])
            context["password"] = password
            context["password_change_url"] = settings.EMAIL_TEMPLATE_PASSWORD_CHANGE_URL
            template = MailTemplate.objects.get(
                code="ACCOUNT_CREATED_BY_MANAGER_CONFIRMATION"
            )
        else:
            SocialAccount.objects.create(
                user=user,
                provider=CASProvider.id,
                uid=user.username,
                extra_data={},
            )
            template = MailTemplate.objects.get(
                code="ACCOUNT_CREATED_BY_MANAGER_CONFIRMATION_LDAP"
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
        if request.user.has_perm("users.view_user_anyone"):
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

        request.data.pop("username", False)

        if user.is_superuser is True or user.is_staff is True:
            return response.Response(
                {"error": _("Cannot edit superuser.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "can_submit_projects" in request.data
            and to_bool(request.data["can_submit_projects"]) is True
            and not self.request.user.has_perm("users.change_user_all_fields")
        ):
            return response.Response(
                {"error": _("Only managers can edit this field.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if user.is_cas_user():
            for restricted_field in [
                "email",
                "first_name",
                "last_name",
            ]:
                request.data.pop(restricted_field, False)
        elif "email" in request.data:
            if request.data["email"].split('@')[1] in settings.RESTRICTED_DOMAINS:
                return response.Response(
                    {
                        "error": _(
                            "This email address cannot be used for a local account."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            request.data.update({"username": request.data["email"]})

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
        elif user.is_validated_by_admin is False:
            assos_user = AssociationUsers.objects.filter(user_id=user.id)

            current_site = get_current_site(request)
            context = {
                "site_domain": current_site.domain,
                "site_name": current_site.name,
                "account_url": f"{settings.EMAIL_TEMPLATE_ACCOUNT_VALIDATE_URL}{user.id}",
            }
            if assos_user.count() > 0:
                template = MailTemplate.objects.get(
                    code="INSTITUTION_MANAGER_LDAP_ACCOUNT_CONFIRMATION"
                )
                managers_emails = list(
                    user.get_user_institutions().values_list("email", flat=True)
                )
            else:
                template = MailTemplate.objects.get(
                    code="MISC_MANAGER_LDAP_ACCOUNT_CONFIRMATION"
                )
                managers_emails = []
                for user_to_check in User.objects.all():
                    if user_to_check.has_perm("view_user_misc"):
                        managers_emails.append(user_to_check.email)
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=managers_emails,
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
