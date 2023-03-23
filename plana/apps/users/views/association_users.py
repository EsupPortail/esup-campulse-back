"""Views linked to links between users and associations."""

import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.institutions.models.institution import Institution
from plana.apps.users.models.user import AssociationUsers, User
from plana.apps.users.serializers.association_users import (
    AssociationUsersCreateSerializer,
    AssociationUsersDeleteSerializer,
    AssociationUsersSerializer,
    AssociationUsersUpdateSerializer,
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
                "institutions",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by Institutions IDs.",
            ),
            OpenApiParameter(
                "association_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by Association ID.",
            ),
        ],
        tags=["users/associations"],
    ),
    post=extend_schema(tags=["users/associations"]),
)
class AssociationUsersListCreate(generics.ListCreateAPIView):
    """/users/associations/ route"""

    def get_queryset(self):
        association_id = self.request.query_params.get("association_id")

        if (
            association_id is not None
            and association_id != ""
            and (
                self.request.user.has_perm("users.view_associationusers_anyone")
                or self.request.user.is_president_in_association(association_id)
            )
        ):
            queryset = AssociationUsers.objects.filter(association_id=association_id)
        elif self.request.user.has_perm("users.view_associationusers_anyone"):
            queryset = AssociationUsers.objects.all()
        else:
            queryset = AssociationUsers.objects.filter(user_id=self.request.user.pk)

        is_validated_by_admin = self.request.query_params.get("is_validated_by_admin")
        institutions = self.request.query_params.get("institutions")

        if is_validated_by_admin is not None and is_validated_by_admin != "":
            queryset = queryset.filter(
                is_validated_by_admin=to_bool(is_validated_by_admin)
            )

        if institutions is not None and institutions != "":
            institutions_ids = institutions.split(",")
            if "" in institutions_ids:
                del institutions_ids[institutions_ids.index("")]
            queryset = queryset.filter(
                association_id__in=Association.objects.filter(
                    institution_id__in=institutions_ids
                ).values_list("id", flat=True)
            )

        return queryset

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "POST":
            self.serializer_class = AssociationUsersCreateSerializer
        elif self.request.method == "GET":
            self.serializer_class = AssociationUsersSerializer
        return super().get_serializer_class()

    def get(self, request, *args, **kwargs):
        """Lists all associations linked to a user, or all associations of all users (manager)."""
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Creates a new link between a user and an association."""
        try:
            username = request.data["user"]
            association_id = request.data["association"]
            user = User.objects.get(username=username)
            association = Association.objects.get(id=association_id)
        except (ObjectDoesNotExist, MultiValueDictKeyError):
            return response.Response(
                {"error": _("No user name or association id given.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.is_anonymous and user.is_validated_by_admin:
            return response.Response(
                {"error": _("Only managers can edit associations for this account.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        association_user = AssociationUsers.objects.filter(
            user_id=user.pk, association_id=association_id
        )
        if association_user.count() > 0:
            return response.Response(
                {"error": _("User already in association.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_superuser or user.is_staff:
            return response.Response(
                {"error": _("A manager cannot have an association.")},
                status=status.HTTP_400_BAD_REQUEST,
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

        if "is_validated_by_admin" in request.data and (
            to_bool(request.data["is_validated_by_admin"]) is True
            and request.user.is_anonymous
            or (
                not request.user.has_perm(
                    "users.change_associationusers_any_institution"
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
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "is_president" in request.data
            and to_bool(request.data["is_president"]) is True
        ):
            association_user_president = AssociationUsers.objects.filter(
                association_id=association_id, is_president=True
            )
            if association_user_president.count() > 0:
                return response.Response(
                    {"error": _("President already in association.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        association_users = AssociationUsers.objects.filter(
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

        if (
            request.user.is_staff
            and not request.user.has_perm(
                "users.change_associationusers_any_institution"
            )
            and not request.user.is_staff_for_association(association_id)
        ):
            return response.Response(
                {"error": _("Cannot add an association from this institution.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.user.is_anonymous and user.is_validated_by_admin:
            if request.user.is_staff:
                request.data["is_validated_by_admin"] = True
            else:
                request.data["is_validated_by_admin"] = False

        if not user.is_validated_by_admin:
            current_site = get_current_site(request)
            context = {
                "site_domain": current_site.domain,
                "site_name": current_site.name,
                "user_association_url": f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_USER_ASSOCIATION_VALIDATE_PATH}{user.pk}",
            }
            template = MailTemplate.objects.get(code="USER_ASSOCIATION_MANAGER_MESSAGE")
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=Institution.objects.get(id=association.institution_id).email,
                subject=template.subject.replace(
                    "{{ site_name }}", context["site_name"]
                ),
                message=template.parse_vars(request.user, request, context),
            )

        return super().create(request, *args, **kwargs)


@extend_schema_view(
    get=extend_schema(tags=["users/associations"]),
)
class AssociationUsersRetrieve(generics.RetrieveAPIView):
    """/users/{user_id}/associations/ route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = AssociationUsers.objects.all()
    serializer_class = AssociationUsersSerializer

    def get(self, request, *args, **kwargs):
        """Retrieves all associations linked to a user (manager)."""
        if (
            request.user.has_perm("users.view_associationusers_anyone")
            or kwargs["user_id"] == request.user.pk
        ):
            serializer = self.serializer_class(
                self.queryset.filter(user_id=kwargs["user_id"]), many=True
            )
        else:
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )
        return response.Response(serializer.data)


@extend_schema(methods=["GET", "PUT"], exclude=True)
@extend_schema_view(
    patch=extend_schema(tags=["users/associations"]),
    delete=extend_schema(tags=["users/associations"]),
)
class AssociationUsersUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/users/{user_id}/associations/{association_id} route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = AssociationUsers.objects.all()

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            self.serializer_class = AssociationUsersUpdateSerializer
        elif self.request.method == "DELETE":
            self.serializer_class = AssociationUsersDeleteSerializer
        return super().get_serializer_class()

    def get(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        """Updates user role in an association (manager and president)."""
        try:
            user = User.objects.get(id=kwargs["user_id"])
            association = Association.objects.get(id=kwargs["association_id"])
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("No user or association found.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            asso_user = self.queryset.get(
                user_id=kwargs["user_id"], association_id=kwargs["association_id"]
            )
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Link between this user and association does not exist.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            president = AssociationUsers.objects.get(
                association_id=kwargs["association_id"], user_id=request.user.pk
            ).is_president
        except ObjectDoesNotExist:
            president = False

        if (
            not request.user.has_perm("users.change_associationusers_any_institution")
            and not request.user.is_staff_for_association(kwargs["association_id"])
            and not request.user.is_president_in_association(kwargs["association_id"])
        ):
            return response.Response(
                {"error": _("No edition rights on this link.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "is_president" in request.data
            and president
            and asso_user.user_id == request.user.pk
        ):
            return response.Response(
                {"error": _("President cannot self-edit.")},
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

        if "is_validated_by_admin" in request.data and (
            not request.user.has_perm("users.change_associationusers_any_institution")
            and not request.user.is_staff_for_association(kwargs["association_id"])
        ):
            return response.Response(
                {
                    "error": _(
                        "Only managers can validate associations for this account."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "is_president" in request.data and to_bool(request.data["is_president"]):
            if request.user.is_staff_for_association(kwargs["association_id"]):
                try:
                    actual_president = AssociationUsers.objects.get(
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
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if (not "can_be_president" in request.data) and (
            "can_be_president_from" in request.data
            or "can_be_president_to" in request.data
        ):
            request.data["can_be_president"] = True

        if (
            "can_be_president_from" in request.data
            and request.data["can_be_president_from"] is not None
            and "can_be_president_to" in request.data
            and request.data["can_be_president_to"] is not None
            and request.data["can_be_president_from"]
            > request.data["can_be_president_to"]
        ):
            return response.Response(
                {"error": _("Can't remove president delegation before giving it.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
            "can_be_president",
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

        if (
            "is_validated_by_admin" in request.data
            and request.data["is_validated_by_admin"] is True
            and (
                request.user.has_perm("users.change_associationusers_any_institution")
                or request.user.is_staff_for_association(kwargs["association_id"])
            )
        ):
            current_site = get_current_site(request)
            context = {
                "site_domain": current_site.domain,
                "site_name": current_site.name,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "association_name": association.name,
            }
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

        return response.Response({}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """Destroys an association linked to a user."""
        try:
            association = Association.objects.get(id=kwargs["association_id"])
            user = User.objects.get(id=kwargs["user_id"])
            request.data["user"] = user.id
            request.data["association"] = association.id
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("No user or association found.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            not request.user.has_perm("users.delete_associationusers_any_institution")
            and not request.user.is_staff_in_institution(association.institution_id)
            and request.user.pk != kwargs["user_id"]
        ):
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        AssociationUsers.objects.filter(
            user_id=kwargs["user_id"], association_id=kwargs["association_id"]
        ).delete()
        if request.user.has_perm(
            "users.delete_associationusers_any_institution"
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
