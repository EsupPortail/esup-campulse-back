"""Views directly linked to projects."""
import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate
from plana.apps.projects.serializers.project import (
    ProjectPartialDataSerializer,
    ProjectRestrictedSerializer,
    ProjectSerializer,
)
from plana.apps.users.models.user import AssociationUser, User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class ProjectListCreate(generics.ListCreateAPIView):
    """/projects/ route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Project.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            self.serializer_class = ProjectSerializer
        else:
            self.serializer_class = ProjectPartialDataSerializer
        return super().get_serializer_class()

    def get(self, request, *args, **kwargs):
        """Lists all projects linked to a user, or all projects with all their details (manager)."""
        if request.user.has_perm("projects.view_project_all"):
            serializer = self.get_serializer(self.queryset.all(), many=True)
            return response.Response(serializer.data)

        user_associations_ids = AssociationUser.objects.filter(
            user_id=request.user.pk
        ).values_list("association_id")
        serializer = self.get_serializer(
            self.queryset.filter(
                models.Q(user_id=request.user.pk)
                | models.Q(association_id__in=user_associations_ids)
            ),
            many=True,
        )
        return response.Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Creates a new project."""
        if (
            "association" in request.data
            and request.data["association"] is not None
            and request.data["association"] != ""
        ):
            try:
                association = Association.objects.get(pk=request.data["association"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("Association does not exist.")},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if association.can_submit_projects:
                try:
                    member = AssociationUser.objects.get(
                        association_id=request.data["association"],
                        user_id=request.user.pk,
                    )
                    if (
                        not member.is_president
                        and not request.user.is_president_in_association(
                            request.data["association"]
                        )
                    ):
                        return response.Response(
                            {"error": _("Not allowed to create a new project.")},
                            status=status.HTTP_403_FORBIDDEN,
                        )
                except ObjectDoesNotExist:
                    return response.Response(
                        {"error": _("Not allowed to create a new project.")},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            else:
                return response.Response(
                    {"error": _("Not allowed to create a new project.")},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if (
            "user" in request.data
            and request.data["user"] is not None
            and request.data["user"] != ""
            and (
                not request.user.can_submit_projects
                or int(request.data["user"]) != request.user.pk
            )
        ):
            return response.Response(
                {"error": _("Not allowed to create a new project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "association" in request.data
            and request.data["association"] is not None
            and request.data["association"] != ""
        ) and (
            "user" in request.data
            and request.data["user"] is not None
            and request.data["user"] != ""
        ):
            return response.Response(
                {"error": _("A project can only have one affectation.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            not "association" in request.data
            or request.data["association"] is None
            or request.data["association"] == ""
        ) and (
            not "user" in request.data
            or request.data["user"] is None
            or request.data["user"] == ""
        ):
            return response.Response(
                {"error": _("Missing affectation of the new project.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data["creation_date"] = datetime.date.today()
        request.data["edition_date"] = datetime.date.today()

        return super().create(request, *args, **kwargs)


@extend_schema(methods=["PUT"], exclude=True)
class ProjectRetrieveUpdate(generics.RetrieveUpdateAPIView):
    """/projects/{id} route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.request.method == "PUT":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        """Retrieves a project with all its details."""
        try:
            project = self.queryset.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm("projects.view_project_all") and (
            (project.user is not None and request.user.pk != project.user)
            or (
                project.association is not None
                and not request.user.is_in_association(project.association)
            )
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        """Updates project details."""
        try:
            project = self.queryset.get(pk=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm("projects.change_project_basic_fields"):
            return response.Response(
                {"error": _("Not allowed to update basic fields for this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not request.user.can_edit_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        expired_project_commission_dates_count = ProjectCommissionDate.objects.filter(
            project_id=project.pk,
            commission_date_id__in=CommissionDate.objects.filter(
                submission_date__lte=datetime.datetime.today()
            ).values_list("id", flat=True),
        ).count()
        if expired_project_commission_dates_count > 0:
            return response.Response(
                {"error": _("Project is linked to expired commissions.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        authorized_status = ["PROJECT_DRAFT", "PROJECT_PROCESSING"]
        if "project_status" in request.data:
            if request.data["project_status"] not in authorized_status:
                return response.Response(
                    {"error": _("Wrong status.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if request.data["project_status"] == "PROJECT_PROCESSING":
                template = None
                managers_emails = []
                current_site = get_current_site(request)
                context = {
                    "site_domain": current_site.domain,
                    "site_name": current_site.name,
                }
                if project.association_id is not None:
                    association = Association.objects.get(id=project.association_id)
                    institution = Institution.objects.get(id=association.institution_id)
                    commissions_misc_used = Commission.objects.filter(
                        id__in=CommissionDate.objects.filter(
                            id__in=ProjectCommissionDate.objects.filter(
                                project_id=project.pk
                            ).values_list("commission_date_id", flat=True)
                        ).values_list("commission_id", flat=True),
                        is_site=False,
                    )
                    context["association_name"] = association.name
                    template = MailTemplate.objects.get(
                        code="NEW_ASSOCIATION_PROJECT_TO_PROCESS"
                    )
                    managers_emails += (
                        institution.default_institution_managers().values_list(
                            "email", flat=True
                        )
                    )
                    if commissions_misc_used.count() > 0:
                        for user_to_check in User.objects.filter(
                            is_superuser=False, is_staff=True
                        ):
                            if user_to_check.has_perm("users.change_user_misc"):
                                managers_emails.append(user_to_check.email)
                elif project.user_id is not None:
                    context["first_name"] = request.user.first_name
                    context["last_name"] = request.user.last_name
                    template = MailTemplate.objects.get(
                        code="NEW_USER_PROJECT_TO_PROCESS"
                    )
                    for user_to_check in User.objects.filter(
                        is_superuser=False, is_staff=True
                    ):
                        if user_to_check.has_perm("users.change_user_misc"):
                            managers_emails.append(user_to_check.email)
                send_mail(
                    from_=settings.DEFAULT_FROM_EMAIL,
                    to_=managers_emails,
                    subject=template.subject.replace(
                        "{{ site_name }}", context["site_name"]
                    ),
                    message=template.parse_vars(request.user, request, context),
                )

        request.data["edition_date"] = datetime.date.today()
        return self.partial_update(request, *args, **kwargs)


@extend_schema(methods=["PUT"], exclude=True)
class ProjectRestrictedUpdate(generics.UpdateAPIView):
    """/projects/{id}/restricted route"""

    queryset = Project.objects.all()
    serializer_class = ProjectRestrictedSerializer

    def get_permissions(self):
        if self.request.method == "PUT":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        """Updates project restricted details (manager only)."""
        try:
            self.queryset.get(pk=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm("projects.change_project_restricted_fields"):
            return response.Response(
                {
                    "error": _(
                        "Not allowed to update restricted fields for this project."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        request.data["edition_date"] = datetime.date.today()
        return self.update(request, *args, **kwargs)
