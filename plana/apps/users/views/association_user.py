"""Views linked to links between users and associations."""
import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.institutions.models.institution import Institution
from plana.apps.users.models.user import AssociationUser, User
from plana.apps.users.serializers.association_user import (
    AssociationUserCreateSerializer,
    AssociationUserDeleteSerializer,
    AssociationUserSerializer,
    AssociationUserUpdateSerializer,
)
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail, to_bool


class AssociationUserListCreate(generics.ListCreateAPIView):
    """/users/associations/ route"""

    queryset = AssociationUser.objects.all()

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "POST":
            self.serializer_class = AssociationUserCreateSerializer
        elif self.request.method == "GET":
            self.serializer_class = AssociationUserSerializer
        return super().get_serializer_class()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "association_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by Association ID.",
            ),
            OpenApiParameter(
                "is_validated_by_admin",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter for members not validated by an admin",
            ),
            OpenApiParameter(
                "institutions",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by Institutions IDs.",
            ),
        ],
        responses={
            status.HTTP_200_OK: AssociationUserSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        },
        tags=["users/associations"],
    )
    def get(self, request, *args, **kwargs):
        """Lists all associations linked to a user, or all associations of all users (manager)."""
        association_id = request.query_params.get("association_id")
        is_validated_by_admin = request.query_params.get("is_validated_by_admin")
        institutions = request.query_params.get("institutions")

        if (
            association_id is not None
            and association_id != ""
            and (
                request.user.has_perm("users.view_associationuser_anyone")
                or request.user.is_president_in_association(association_id)
            )
        ):
            self.queryset = self.queryset.filter(association_id=association_id)
        elif not request.user.has_perm("users.view_associationuser_anyone"):
            self.queryset = self.queryset.filter(user_id=request.user.pk)

        if is_validated_by_admin is not None and is_validated_by_admin != "":
            self.queryset = self.queryset.filter(
                is_validated_by_admin=to_bool(is_validated_by_admin)
            )

        if institutions is not None and institutions != "":
            institutions_ids = institutions.split(",")
            institutions_ids = [
                institution_id
                for institution_id in institutions_ids
                if institution_id != "" and institution_id.isdigit()
            ]
            self.queryset = self.queryset.filter(
                association_id__in=Association.objects.filter(
                    institution_id__in=institutions_ids
                ).values_list("id")
            )

        return self.list(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: AssociationUserCreateSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["users/associations"],
    )
    def post(self, request, *args, **kwargs):
        """Creates a new link between a user and an association."""
        try:
            username = request.data["user"]
            association_id = request.data["association"]
            user = User.objects.get(username=username)
            association = Association.objects.get(id=association_id)
        except (ObjectDoesNotExist, MultiValueDictKeyError):
            return response.Response(
                {"error": _("User or association does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.is_anonymous and user.is_validated_by_admin:
            return response.Response(
                {"error": _("Only managers can edit associations for this account.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            request.user.is_staff
            and not request.user.has_perm(
                "users.change_associationuser_any_institution"
            )
            and not request.user.is_staff_for_association(association_id)
        ):
            return response.Response(
                {"error": _("Cannot add an association from this institution.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if "is_validated_by_admin" in request.data and (
            to_bool(request.data["is_validated_by_admin"]) is True
            and request.user.is_anonymous
            or (
                not request.user.has_perm(
                    "users.change_associationuser_any_institution"
                )
                and not request.user.is_staff_for_association(association_id)
            )
        ):
            return response.Response(
                {
                    "error": _(
                        "Only managers can validate associations for this account."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        has_associations_possible_group = False
        for group in user.get_user_groups():
            if settings.GROUPS_STRUCTURE[group.name]["ASSOCIATIONS_POSSIBLE"] is True:
                has_associations_possible_group = True
        if not has_associations_possible_group:
            return response.Response(
                {"error": _("The user hasn't any group that can have associations.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        association_users = AssociationUser.objects.filter(
            association_id=association_id
        )
        if (
            not association.amount_members_allowed is None
            and association_users.count() >= association.amount_members_allowed
        ):
            return response.Response(
                {"error": _("Too many users in association.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        association_user = AssociationUser.objects.filter(
            user_id=user.id, association_id=association_id
        )
        if association_user.count() > 0:
            return response.Response(
                {"error": _("User already in association.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "is_president" in request.data
            and to_bool(request.data["is_president"]) is True
        ):
            association_user_president = AssociationUser.objects.filter(
                association_id=association_id, is_president=True
            )
            if association_user_president.count() > 0:
                return response.Response(
                    {"error": _("President already in association.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if not request.user.is_anonymous and user.is_validated_by_admin:
            if request.user.is_staff:
                request.data["is_validated_by_admin"] = True
            else:
                request.data["is_validated_by_admin"] = False

        if "is_validated_by_admin" not in request.data or (
            "is_validated_by_admin" in request.data
            and (to_bool(request.data["is_validated_by_admin"]) is False)
        ):
            current_site = get_current_site(request)
            context = {
                "site_domain": current_site.domain,
                "site_name": current_site.name,
                "user_association_url": f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_USER_ASSOCIATION_VALIDATE_PATH}",
            }
            template = MailTemplate.objects.get(code="USER_ASSOCIATION_MANAGER_MESSAGE")
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=list(
                    Institution.objects.get(id=association.institution_id)
                    .default_institution_managers()
                    .values_list("email", flat=True)
                ),
                subject=template.subject.replace(
                    "{{ site_name }}", context["site_name"]
                ),
                message=template.parse_vars(request.user, request, context),
            )

        return super().create(request, *args, **kwargs)


class AssociationUserRetrieve(generics.RetrieveAPIView):
    """/users/{user_id}/associations/ route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = AssociationUser.objects.all()
    serializer_class = AssociationUserSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: AssociationUserSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["users/associations"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieves all associations linked to a user (manager)."""
        try:
            User.objects.get(id=kwargs["user_id"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("User does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            request.user.has_perm("users.view_associationuser_anyone")
            or kwargs["user_id"] == request.user.pk
        ):
            serializer = self.serializer_class(
                self.queryset.filter(user_id=kwargs["user_id"]), many=True
            )
        else:
            return response.Response(
                {
                    "error": _(
                        "Not allowed to get this link between association and user."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        return response.Response(serializer.data)


class AssociationUserUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/users/{user_id}/associations/{association_id} route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = AssociationUser.objects.all()

    def get_permissions(self):
        if self.request.method in ("GET", "PUT"):
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            self.serializer_class = AssociationUserUpdateSerializer
        elif self.request.method == "DELETE":
            self.serializer_class = AssociationUserDeleteSerializer
        return super().get_serializer_class()

    @extend_schema(
        exclude=True,
        responses={
            status.HTTP_405_METHOD_NOT_ALLOWED: None,
        },
    )
    def get(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
            status.HTTP_200_OK: AssociationUserUpdateSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["users/associations"],
    )
    def patch(self, request, *args, **kwargs):
        """Updates user role in an association (manager and president)."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=kwargs["user_id"])
            association = Association.objects.get(id=kwargs["association_id"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("User or association does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            asso_user = self.queryset.get(
                user_id=kwargs["user_id"], association_id=kwargs["association_id"]
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Link between this user and association does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            president = AssociationUser.objects.get(
                association_id=kwargs["association_id"], user_id=request.user.pk
            ).is_president
        except ObjectDoesNotExist:
            president = False

        if (
            not request.user.has_perm("users.change_associationuser_any_institution")
            and not request.user.is_staff_for_association(kwargs["association_id"])
            and not request.user.is_president_in_association(kwargs["association_id"])
        ):
            return response.Response(
                {"error": _("Not allowed to edit this link.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if "is_validated_by_admin" in request.data and (
            not request.user.has_perm("users.change_associationuser_any_institution")
            and not request.user.is_staff_for_association(kwargs["association_id"])
        ):
            return response.Response(
                {
                    "error": _(
                        "Only managers can validate associations for this account."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "is_president" in request.data
            and president
            and asso_user.user_id == request.user.pk
        ):
            return response.Response(
                {"error": _("President cannot self-edit.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if "is_president" in request.data and to_bool(request.data["is_president"]):
            if request.user.is_staff_for_association(kwargs["association_id"]):
                try:
                    actual_president = AssociationUser.objects.get(
                        association_id=kwargs["association_id"], is_president=True
                    )
                    actual_president.is_president = False
                    actual_president.save()
                except ObjectDoesNotExist:
                    pass
                request.data["is_vice_president"] = False
                request.data["is_secretary"] = False
                request.data["is_treasurer"] = False
            else:
                return response.Response(
                    {"error": _("Only managers can edit president.")},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if (
            "can_be_president_from" in request.data
            and request.data["can_be_president_from"] is not None
            and "can_be_president_to" in request.data
            and request.data["can_be_president_to"] is not None
            and datetime.datetime.strptime(
                request.data["can_be_president_from"], "%Y-%m-%d"
            )
            > datetime.datetime.strptime(
                request.data["can_be_president_to"], "%Y-%m-%d"
            )
        ):
            return response.Response(
                {"error": _("Can't remove president delegation before giving it.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "can_be_president_from" in request.data
            and not "can_be_president_to" in request.data
        ):
            request.data["can_be_president_to"] = None

        if (
            "can_be_president_to" in request.data
            and not "can_be_president_from" in request.data
        ):
            request.data["can_be_president_from"] = datetime.date.today()

        if (
            "is_vice_president" in request.data
            and to_bool(request.data["is_vice_president"]) is True
        ):
            request.data["is_president"] = False
            request.data["is_secretary"] = False
            request.data["is_treasurer"] = False

        if (
            "is_secretary" in request.data
            and to_bool(request.data["is_secretary"]) is True
        ):
            request.data["is_president"] = False
            request.data["is_vice_president"] = False
            request.data["is_treasurer"] = False

        if (
            "is_treasurer" in request.data
            and to_bool(request.data["is_treasurer"]) is True
        ):
            request.data["is_president"] = False
            request.data["is_vice_president"] = False
            request.data["is_secretary"] = False

        fields = [
            "is_president",
            "can_be_president_from",
            "can_be_president_to",
            "is_validated_by_admin",
            "is_vice_president",
            "is_secretary",
            "is_treasurer",
        ]
        for field in fields:
            if field in request.data:
                if field not in [
                    "can_be_president_from",
                    "can_be_president_to",
                ]:
                    setattr(asso_user, field, to_bool(request.data[field]))
                else:
                    setattr(asso_user, field, request.data[field])

        asso_user.save()

        current_site = get_current_site(request)
        context = {
            "site_domain": current_site.domain,
            "site_name": current_site.name,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "association_name": association.name,
        }

        if (
            "is_validated_by_admin" in request.data
            and request.data["is_validated_by_admin"] is True
            and (
                request.user.has_perm("users.change_associationuser_any_institution")
                or request.user.is_staff_for_association(kwargs["association_id"])
            )
        ):
            template = MailTemplate.objects.get(
                code="USER_ASSOCIATION_STUDENT_MESSAGE_CONFIRMATION"
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
            "can_be_president_from" in request.data
            and "can_be_president_to" in request.data
            and (
                request.data["can_be_president_from"] is not None
                or request.data["can_be_president_to"] is not None
            )
        ):
            template = MailTemplate.objects.get(
                code="USER_ASSOCIATION_CAN_BE_PRESIDENT_CONFIRMATION"
            )
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=user.email,
                subject=template.subject.replace(
                    "{{ site_name }}", context["site_name"]
                ),
                message=template.parse_vars(request.user, request, context),
            )

        return response.Response({}, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: AssociationUserDeleteSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["users/associations"],
    )
    def delete(self, request, *args, **kwargs):
        """Destroys an association linked to a user."""
        try:
            association = Association.objects.get(id=kwargs["association_id"])
            user = User.objects.get(id=kwargs["user_id"])
            request.data["user"] = user.id
            request.data["association"] = association.id
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("User or association does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            not request.user.has_perm("users.delete_associationuser_any_institution")
            and not request.user.is_staff_in_institution(association.institution_id)
            and request.user.pk != kwargs["user_id"]
        ):
            return response.Response(
                {
                    "error": _(
                        "Not allowed to delete this link between association and user."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        AssociationUser.objects.filter(
            user_id=kwargs["user_id"], association_id=kwargs["association_id"]
        ).delete()
        if request.user.has_perm(
            "users.delete_associationuser_any_institution"
        ) or request.user.is_staff_for_association(kwargs["association_id"]):
            current_site = get_current_site(request)
            context = {
                "site_domain": current_site.domain,
                "site_name": current_site.name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "association_name": association.name,
            }
            template = MailTemplate.objects.get(
                code="USER_ASSOCIATION_STUDENT_MESSAGE_REJECTION"
            )
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=user.email,
                subject=template.subject.replace(
                    "{{ site_name }}", context["site_name"]
                ),
                message=template.parse_vars(request.user, request, context),
            )
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
