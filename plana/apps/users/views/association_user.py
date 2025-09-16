"""Views linked to links between users and associations."""

import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, response, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.history.models.history import History
from plana.apps.users.models.user import AssociationUser, User
from plana.apps.users.permissions import ViewAssociationUserPermission, AddAssociationUserPermission
from plana.apps.users.serializers.association_user import (
    AssociationUserCreateSerializer,
    AssociationUserSerializer,
    AssociationUserUpdateSerializer,
)
from plana.decorators import capture_queries
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail, to_bool


@extend_schema_view(
    get=extend_schema(
        operation_id="association_user_full_list",
        tags=["users/associations"]
    ),
    post=extend_schema(
        operation_id="association_user_create",
        tags=["users/associations"]
    )
)
class AssociationUserListCreate(generics.ListCreateAPIView):
    """
    /users/associations/ route.
    GET : Retrieves all links between validated users and associations for managers, only the ones authorized
    """

    queryset = AssociationUser.objects.filter(user__is_validated_by_admin=True).select_related('association', 'user')
    filterset_fields = ["is_validated_by_admin"]

    def get_queryset(self):
        return self.queryset.filter(association__in=Association.objects.managed_by_user(self.request.user))

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsAuthenticated, AddAssociationUserPermission]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "POST":
            self.serializer_class = AssociationUserCreateSerializer
        elif self.request.method == "GET":
            self.serializer_class = AssociationUserSerializer
        return super().get_serializer_class()


@extend_schema_view(
    get=extend_schema(
        operation_id="association_user_list_by_user",
        tags=["users/associations"]
    )
)
class AssociationUserRetrieve(generics.ListAPIView):
    """
    /users/{user_id}/associations/ route.
    Used to retrieve associations of given user id
    (All if auth user, only authorized ones if manager)
    """

    permission_classes = [IsAuthenticated, DjangoModelPermissions, ViewAssociationUserPermission]
    queryset = AssociationUser.objects.all().select_related('association', 'user')
    serializer_class = AssociationUserSerializer

    def get_queryset(self):
        user_id = self.kwargs.get("user_id")
        get_object_or_404(User.objects.all(), pk=user_id)
        if user_id == self.request.user.pk:
            return self.queryset.filter(user_id=user_id)
        return self.queryset.filter(
            user_id=user_id,
            association__in=Association.objects.managed_by_user(self.request.user)
        )


class AssociationUserUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/users/{user_id}/associations/{association_id} route."""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = AssociationUser.objects.all()
    serializer_class = AssociationUserUpdateSerializer
    http_method_names = ["patch", "delete"]

    @extend_schema(
        responses={
            status.HTTP_200_OK: None,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["users/associations"],
    )
    def patch(self, request, *args, **kwargs):
        """Update user role in an association (manager and president)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(id=kwargs["user_id"])
            association = Association.objects.get(id=kwargs["association_id"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("User or association does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        asso_user = get_object_or_404(
            self.get_queryset(),
            user_id=kwargs["user_id"],
            association_id=kwargs["association_id"]
        )

        try:
            president = AssociationUser.objects.get(
                association_id=kwargs["association_id"], user_id=request.user.pk
            ).is_president
        except AssociationUser.DoesNotExist:
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
                {"error": _("Only managers can validate associations for this account.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if "is_president" in request.data and president and asso_user.user_id == request.user.pk:
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
            and datetime.datetime.strptime(request.data["can_be_president_from"], "%Y-%m-%d")
            > datetime.datetime.strptime(request.data["can_be_president_to"], "%Y-%m-%d")
        ):
            return response.Response(
                {"error": _("Can't remove president delegation before giving it.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "can_be_president_from" in request.data and not "can_be_president_to" in request.data:
            request.data["can_be_president_to"] = None

        if "can_be_president_to" in request.data and not "can_be_president_from" in request.data:
            request.data["can_be_president_from"] = datetime.date.today()

        if "is_vice_president" in request.data and to_bool(request.data["is_vice_president"]):
            request.data["is_president"] = False
            request.data["is_secretary"] = False
            request.data["is_treasurer"] = False

        if "is_secretary" in request.data and to_bool(request.data["is_secretary"]):
            request.data["is_president"] = False
            request.data["is_vice_president"] = False
            request.data["is_treasurer"] = False

        if "is_treasurer" in request.data and to_bool(request.data["is_treasurer"]):
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
            and request.data["is_validated_by_admin"]
            and (
                request.user.has_perm("users.change_associationuser_any_institution")
                or request.user.is_staff_for_association(kwargs["association_id"])
            )
        ):
            History.objects.create(
                action_title="ASSOCIATION_USER_VALIDATED",
                action_user_id=request.user.pk,
                association_user_id=asso_user.id,
            )
            template = MailTemplate.objects.get(code="USER_ACCOUNT_ASSOCIATION_USER_CONFIRMATION")
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=user.email,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(request.user, request, context),
            )

        if (
            "can_be_president_from" in request.data
            and "can_be_president_to" in request.data
            and (request.data["can_be_president_from"] is not None or request.data["can_be_president_to"] is not None)
        ):
            History.objects.create(
                action_title="ASSOCIATION_USER_DELEGATION_CHANGED",
                action_user_id=request.user.pk,
                association_user_id=asso_user.id,
            )
            template = MailTemplate.objects.get(code="USER_ACCOUNT_ASSOCIATION_PRESIDENT_CONFIRMATION")
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=user.email,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(request.user, request, context),
            )
        elif "is_validated_by_admin" not in request.data:
            History.objects.create(
                action_title="ASSOCIATION_USER_CHANGED",
                action_user_id=request.user.pk,
                association_user_id=asso_user.id,
            )

        return response.Response({}, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: AssociationUserUpdateSerializer,
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
                {"error": _("Not allowed to delete this link between association and user.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        AssociationUser.objects.filter(user_id=kwargs["user_id"], association_id=kwargs["association_id"]).delete()
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
            template = MailTemplate.objects.get(code="USER_ACCOUNT_ASSOCIATION_USER_REJECTION")
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=user.email,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(request.user, request, context),
            )
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
