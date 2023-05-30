"""Views directly linked to users and their links with other models."""
import datetime

from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress
from allauth.account.utils import user_pk_to_url_str
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.institutions.models.institution import Institution
from plana.apps.users.models.user import (
    AssociationUser,
    GroupInstitutionCommissionUser,
    User,
)
from plana.apps.users.provider import CASProvider
from plana.apps.users.serializers.user import (
    UserPartialDataSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail, to_bool


class UserListCreate(generics.ListCreateAPIView):
    """/users/ route"""

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

    def get_serializer_class(self):
        if not self.request.user.has_perm(
            "users.view_user_anyone"
        ) and not self.request.user.has_perm("users.view_user_misc"):
            self.serializer_class = UserPartialDataSerializer
        else:
            self.serializer_class = UserSerializer
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
        """Lists users sharing the same association, or all users (manager)."""
        name = request.query_params.get("name")
        email = request.query_params.get("email")
        is_validated_by_admin = request.query_params.get("is_validated_by_admin")
        is_cas = request.query_params.get("is_cas")
        association_id = request.query_params.get("association_id")
        institutions = request.query_params.get("institutions")

        if not request.user.has_perm(
            "users.view_user_anyone"
        ) and not request.user.has_perm("users.view_user_misc"):
            self.queryset = self.queryset.filter(
                id__in=AssociationUser.objects.filter(
                    association_id__in=request.user.get_user_associations().values_list(
                        "id"
                    )
                ).values_list("user_id")
            )
        else:
            if name is not None and name != "":
                name = str(name).strip()
                self.queryset = self.queryset.filter(
                    Q(first_name__nospaces__unaccent__icontains=name.replace(" ", ""))
                    | Q(last_name__nospaces__unaccent__icontains=name.replace(" ", ""))
                )

            if email is not None and email != "":
                email = str(email).strip()
                self.queryset = self.queryset.filter(
                    email__nospaces__unaccent__icontains=email.replace(" ", "")
                )

            if is_validated_by_admin is not None and is_validated_by_admin != "":
                is_validated_by_admin = to_bool(is_validated_by_admin)
                email_validated_user_ids = EmailAddress.objects.filter(
                    verified=True
                ).values_list("user_id")
                self.queryset = self.queryset.filter(
                    is_validated_by_admin=is_validated_by_admin,
                    id__in=email_validated_user_ids,
                )

            if is_cas is not None and is_cas != "":
                is_cas = to_bool(is_cas)
                cas_ids_list = SocialAccount.objects.filter(provider='cas').values_list(
                    "user_id"
                )
                self.queryset = (
                    self.queryset.filter(id__in=cas_ids_list)
                    if is_cas
                    else self.queryset.exclude(id__in=cas_ids_list)
                )

            if association_id is not None and association_id != "":
                assos_users_query = AssociationUser.objects.filter(
                    association_id=association_id
                ).values_list("user_id")
                self.queryset = self.queryset.filter(id__in=assos_users_query)

            if institutions is not None:
                misc_users_query = User.objects.filter(
                    Q(
                        id__in=GroupInstitutionCommissionUser.objects.filter(
                            institution_id__isnull=True, commission_id__isnull=True
                        ).values_list("user_id")
                    )
                    & ~Q(id__in=AssociationUser.objects.all().values_list("user_id"))
                )
                commission_users_query = User.objects.filter(
                    id__in=GroupInstitutionCommissionUser.objects.filter(
                        commission_id__isnull=False
                    ).values_list("user_id")
                ).values_list("id")
                if institutions == "":
                    self.queryset = self.queryset.filter(
                        Q(id__in=misc_users_query) | Q(id__in=commission_users_query)
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

                    associations_ids = Association.objects.filter(
                        institution_id__in=institutions_ids
                    ).values_list("id")
                    assos_users_query = AssociationUser.objects.filter(
                        association_id__in=associations_ids
                    ).values_list("user_id")

                    if check_other_users is True:
                        self.queryset = self.queryset.filter(
                            Q(id__in=assos_users_query)
                            | Q(id__in=misc_users_query)
                            | Q(id__in=commission_users_query)
                        )
                    else:
                        self.queryset = self.queryset.filter(id__in=assos_users_query)

        return self.list(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: UserSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        }
    )
    def post(self, request, *args, **kwargs):
        """Create an account for another person (manager only)."""
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

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
            context[
                "password_change_url"
            ] = f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_PASSWORD_CHANGE_PATH}"
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


class UserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/users/{id} route"""

    queryset = User.objects.all()

    def get_permissions(self):
        if self.request.method == "PUT":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = UserSerializer
        else:
            self.serializer_class = UserUpdateSerializer
        return super().get_serializer_class()

    @extend_schema(
        responses={
            status.HTTP_200_OK: UserSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Retrieves a user with all details."""
        try:
            self.queryset.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("User does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm(
            "users.view_user_anyone"
        ) and not self.request.user.has_perm("users.view_user_misc"):
            return response.Response(
                {"error": _("Not allowed to retrieve this user.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        exclude=True,
        responses={
            status.HTTP_405_METHOD_NOT_ALLOWED: None,
        },
    )
    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(
        responses={
            status.HTTP_200_OK: UserUpdateSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def patch(self, request, *args, **kwargs):
        """Updates a user field (with a restriction on CAS auto-generated fields)."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("User does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        request.data.pop("username", False)

        if user.is_superuser is True or user.is_staff is True:
            return response.Response(
                {"error": _("Cannot edit superuser.")},
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

        current_site = get_current_site(request)
        context = {
            "site_domain": current_site.domain,
            "site_name": current_site.name,
            "manager_email_address": request.user.email,
        }

        if "can_submit_projects" in request.data:
            template = None
            if to_bool(request.data["can_submit_projects"]) is False:
                template = MailTemplate.objects.get(
                    code="DEACTIVATE_PROJECT_SUBMISSION"
                )
            elif to_bool(request.data["can_submit_projects"]) is True:
                template = MailTemplate.objects.get(
                    code="REACTIVATE_PROJECT_SUBMISSION"
                )
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=user.email,
                subject=template.subject.replace(
                    "{{ site_name }}", context["site_name"]
                ),
                message=template.parse_vars(request.user, request, context),
            )

        if (
            "is_validated_by_admin" in request.data
            and to_bool(request.data["is_validated_by_admin"]) is True
        ):
            context["username"] = user.username
            context["first_name"] = user.first_name
            context["last_name"] = user.last_name
            context["documentation_url"] = settings.APP_DOCUMENTATION_URL
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
                ] = f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_PASSWORD_RESET_PATH}?uid={uid}&token={token}"
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=user.email,
                subject=template.subject.replace(
                    "{{ site_name }}", context["site_name"]
                ),
                message=template.parse_vars(user, request, context),
            )

            unvalidated_assos_user = AssociationUser.objects.filter(
                user_id=user.id, is_validated_by_admin=False
            )
            if unvalidated_assos_user.count() > 0:
                for unvalidated_asso_user in unvalidated_assos_user:
                    context[
                        "user_association_url"
                    ] = f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_USER_ASSOCIATION_VALIDATE_PATH}"
                    template = MailTemplate.objects.get(
                        code="USER_ASSOCIATION_MANAGER_MESSAGE"
                    )
                    send_mail(
                        from_=settings.DEFAULT_FROM_EMAIL,
                        to_=list(
                            Institution.objects.get(
                                id=unvalidated_asso_user.association.institution_id
                            )
                            .default_institution_managers()
                            .values_list("email", flat=True)
                        ),
                        subject=template.subject.replace(
                            "{{ site_name }}", context["site_name"]
                        ),
                        message=template.parse_vars(request.user, request, context),
                    )

        return self.partial_update(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: UserUpdateSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def delete(self, request, *args, **kwargs):
        """Destroys a user from the database (with a restriction on manager users)."""
        try:
            user = User.objects.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("User does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
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
