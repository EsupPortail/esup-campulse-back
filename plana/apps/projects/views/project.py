"""Views directly linked to projects."""
import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models.commission_date import Commission
from plana.apps.commissions.models.fund import Fund
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate
from plana.apps.projects.serializers.project import (
    ProjectPartialDataSerializer,
    ProjectReviewSerializer,
    ProjectReviewUpdateSerializer,
    ProjectSerializer,
    ProjectStatusSerializer,
    ProjectUpdateManagerSerializer,
    ProjectUpdateSerializer,
)
from plana.apps.users.models.user import AssociationUser, User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail, to_bool


class ProjectListCreate(generics.ListCreateAPIView):
    """/projects/ route"""

    filter_backends = [filters.SearchFilter]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    search_fields = [
        "name__nospaces__unaccent",
        "creation_date__year",
        "user_id",
        "association_id",
        "commission_dates",
    ]

    def get_queryset(self):
        return Project.visible_objects.all().order_by("edition_date")

    def get_serializer_class(self):
        if self.request.method == "POST":
            self.serializer_class = ProjectUpdateSerializer
        else:
            self.serializer_class = ProjectPartialDataSerializer
        return super().get_serializer_class()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by name.",
            ),
            OpenApiParameter(
                "year",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by creation_date year.",
            ),
            OpenApiParameter(
                "user_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by User ID.",
            ),
            OpenApiParameter(
                "association_id",
                OpenApiTypes.INT,
                OpenApiParameter.QUERY,
                description="Filter by Association ID.",
            ),
            OpenApiParameter(
                "project_statuses",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by Project Statuses codes.",
            ),
            OpenApiParameter(
                "commission_dates",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by Commission Dates linked to a project.",
            ),
            OpenApiParameter(
                "with_comments",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter to get projects where comments are posted.",
            ),
            OpenApiParameter(
                "active_projects",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Filter to get projects where reviews are still pending.",
            ),
        ],
        responses={
            status.HTTP_200_OK: ProjectPartialDataSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Lists all projects linked to a user, or all projects with all their details (manager)."""
        queryset = self.get_queryset()

        name = request.query_params.get("name")
        year = request.query_params.get("year")
        user = request.query_params.get("user_id")
        association = request.query_params.get("association_id")
        project_statuses = request.query_params.get("project_statuses")
        commission_dates = request.query_params.get("commission_dates")
        with_comments = request.query_params.get("with_comments")
        active_projects = request.query_params.get("active_projects")

        if name is not None and name != "":
            name = str(name).strip()
            queryset = queryset.filter(
                name__nospaces__unaccent__icontains=name.replace(" ", "")
            )

        if year is not None and year != "":
            queryset = queryset.filter(creation_date__year=year)

        if not request.user.has_perm("projects.view_project_any_fund"):
            if request.user.is_staff:
                user_funds_ids = request.user.get_user_managed_funds()
            else:
                user_funds_ids = request.user.get_user_funds()
        else:
            user_funds_ids = Fund.objects.all().values_list("id")

        if not request.user.has_perm("projects.view_project_any_institution"):
            user_institutions_ids = request.user.get_user_managed_institutions()
        else:
            user_institutions_ids = Institution.objects.all().values_list("id")

        if not request.user.has_perm(
            "projects.view_project_any_fund"
        ) or not request.user.has_perm("projects.view_project_any_institution"):
            user_associations_ids = request.user.get_user_associations()
            user_projects_ids = Project.visible_objects.filter(
                models.Q(user_id=request.user.pk)
                | models.Q(association_id__in=user_associations_ids)
            ).values_list("id")

            queryset = queryset.filter(
                models.Q(id__in=user_projects_ids)
                | models.Q(
                    id__in=(
                        ProjectCommissionDate.objects.filter(
                            commission_date_id__in=Commission.objects.filter(
                                commission_id__in=user_funds_ids
                            ).values_list("id")
                        ).values_list("project_id")
                    )
                )
                | models.Q(
                    association_id__in=Association.objects.filter(
                        institution_id__in=user_institutions_ids
                    ).values_list("id")
                )
            )

        if user is not None and user != "":
            queryset = queryset.filter(user_id=user)

        if association is not None and association != "":
            queryset = queryset.filter(association_id=association)

        if project_statuses is not None and project_statuses != "":
            all_project_statuses = [c[0] for c in Project.project_status.field.choices]
            project_statuses_codes = project_statuses.split(",")
            project_statuses_codes = [
                project_status_code
                for project_status_code in project_statuses_codes
                if project_status_code != ""
                and project_status_code in all_project_statuses
            ]
            queryset = queryset.filter(project_status__in=project_statuses_codes)

        if commission_dates is not None and commission_dates != "":
            commission_dates_ids = commission_dates.split(",")
            commission_dates_ids = [
                commission_date_id
                for commission_date_id in commission_dates
                if commission_date_id != "" and commission_date_id.isdigit()
            ]
            queryset = queryset.filter(
                id__in=ProjectCommissionDate.objects.filter(
                    commission_date_id__in=commission_dates_ids
                ).values_list("project_id")
            )

        if with_comments is not None and with_comments != "":
            projects_ids_with_comments = ProjectComment.objects.all().values_list(
                "project_id"
            )
            if to_bool(with_comments) is False:
                queryset = queryset.exclude(id__in=projects_ids_with_comments)
            else:
                queryset = queryset.filter(id__in=projects_ids_with_comments)

        if active_projects is not None and active_projects != "":
            inactive_statuses = Project.ProjectStatus.get_archived_project_statuses()
            if to_bool(active_projects) is False:
                queryset = queryset.filter(project_status__in=inactive_statuses)
            else:
                queryset = queryset.exclude(project_status__in=inactive_statuses)

        serializer = self.get_serializer_class()(queryset, many=True)
        return response.Response(serializer.data)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: ProjectSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    def post(self, request, *args, **kwargs):
        """Creates a new project."""
        if (
            "association" in request.data
            and request.data["association"] is not None
            and request.data["association"] != ""
        ):
            try:
                association = Association.objects.get(id=request.data["association"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("Association does not exist.")},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if association.can_submit_projects and association.is_enabled:
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
                    ) or not request.user.has_perm("projects.add_project_association"):
                        return response.Response(
                            {
                                "error": _(
                                    "User not allowed to create a new project for this association."
                                )
                            },
                            status=status.HTTP_403_FORBIDDEN,
                        )
                except ObjectDoesNotExist:
                    return response.Response(
                        {"error": _("User not allowed in this association.")},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            else:
                return response.Response(
                    {"error": _("Association not allowed to create a new project.")},
                    status=status.HTTP_403_FORBIDDEN,
                )

        if (
            "user" in request.data
            and request.data["user"] is not None
            and request.data["user"] != ""
            and (
                not request.user.can_submit_projects
                or not request.user.is_active
                or int(request.data["user"]) != request.user.pk
                or not request.user.has_perm("projects.add_project_user")
            )
        ):
            return response.Response(
                {"error": _("User not allowed to create a new project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
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

        if (
            "amount_students_audience" in request.data
            and "amount_all_audience" in request.data
            and int(request.data["amount_students_audience"])
            > int(request.data["amount_all_audience"])
        ):
            return response.Response(
                {
                    "error": _(
                        "Number of students in audience cannot exceed number of all people in audience."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "planned_start_date" in request.data
            and "planned_end_date" in request.data
            and datetime.datetime.strptime(
                request.data["planned_start_date"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            > datetime.datetime.strptime(
                request.data["planned_end_date"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        ):
            return response.Response(
                {"error": _("Can't set planned start date after planned end date.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data["creation_date"] = datetime.date.today()
        request.data["edition_date"] = datetime.date.today()

        return super().create(request, *args, **kwargs)


class ProjectRetrieveUpdate(generics.RetrieveUpdateAPIView):
    """/projects/{id} route"""

    def get_permissions(self):
        if self.request.method == "PUT":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_queryset(self):
        return Project.visible_objects.all()

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            if self.request.user.has_perm("projects.change_project_as_bearer"):
                self.serializer_class = ProjectUpdateSerializer
            elif self.request.user.has_perm("projects.change_project_as_validator"):
                self.serializer_class = ProjectUpdateManagerSerializer
            # TODO OpenAPI problem if no serializer given.
            else:
                self.serializer_class = ProjectSerializer
        else:
            self.serializer_class = ProjectSerializer
        return super().get_serializer_class()

    @extend_schema(
        responses={
            status.HTTP_200_OK: ProjectSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Retrieves a project with all its details."""
        try:
            project = self.get_queryset().get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            not request.user.has_perm("projects.view_project_any_fund")
            and not request.user.has_perm("projects.view_project_any_institution")
            and not request.user.can_access_project(project)
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this project.")},
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
            status.HTTP_200_OK: ProjectSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    def patch(self, request, *args, **kwargs):
        """Updates project details."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = self.get_queryset().get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.can_access_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        expired_project_commission_dates_count = ProjectCommissionDate.objects.filter(
            project_id=project.id,
            commission_date_id__in=Commission.objects.filter(
                submission_date__lte=datetime.datetime.today()
            ).values_list("id"),
        ).count()
        if expired_project_commission_dates_count > 0:
            return response.Response(
                {"error": _("Project is linked to expired commissions.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "amount_students_audience" in request.data
            and "amount_all_audience" in request.data
            and int(request.data["amount_students_audience"])
            > int(request.data["amount_all_audience"])
        ):
            return response.Response(
                {
                    "error": _(
                        "Number of students in audience cannot exceed number of all people in audience."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "planned_start_date" in request.data
            and "planned_end_date" in request.data
            and datetime.datetime.strptime(
                request.data["planned_start_date"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            > datetime.datetime.strptime(
                request.data["planned_end_date"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        ):
            return response.Response(
                {"error": _("Can't set planned start date after planned end date.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data["edition_date"] = datetime.date.today()
        return self.partial_update(request, *args, **kwargs)


class ProjectReviewRetrieveUpdate(generics.RetrieveUpdateAPIView):
    """/projects/{id}/review route"""

    def get_permissions(self):
        if self.request.method == "PUT":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_queryset(self):
        return Project.visible_objects.all()

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            self.serializer_class = ProjectReviewUpdateSerializer
        else:
            self.serializer_class = ProjectReviewSerializer
        return super().get_serializer_class()

    @extend_schema(
        responses={
            status.HTTP_200_OK: ProjectSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Retrieves a project review with all its details."""
        try:
            project = self.get_queryset().get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            not request.user.has_perm("projects.view_project_any_fund")
            and not request.user.has_perm("projects.view_project_any_institution")
            and not request.user.can_access_project(project)
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this project.")},
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
            status.HTTP_200_OK: ProjectSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    def patch(self, request, *args, **kwargs):
        """Updates project details."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = self.get_queryset().get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm("projects.change_project_as_bearer"):
            return response.Response(
                {"error": _("Not allowed to update bearer fields for this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not request.user.can_access_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "real_start_date" in request.data
            and "real_end_date" in request.data
            and datetime.datetime.strptime(
                request.data["real_start_date"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            > datetime.datetime.strptime(
                request.data["real_end_date"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        ):
            return response.Response(
                {"error": _("Can't set start date after end date.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pending_commission_dates_count = ProjectCommissionDate.objects.filter(
            project_id=kwargs["pk"],
            commission_date_id__in=Commission.objects.filter(
                commission_date__gt=datetime.datetime.now()
            ).values_list("id"),
        ).count()
        if pending_commission_dates_count > 0:
            return response.Response(
                {
                    "error": _(
                        "Cannot edit review if commission dates are still pending."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data["edition_date"] = datetime.date.today()
        return self.partial_update(request, *args, **kwargs)


class ProjectStatusUpdate(generics.UpdateAPIView):
    """/projects/{id}/status route"""

    serializer_class = ProjectStatusSerializer

    def get_permissions(self):
        if self.request.method == "PUT":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_queryset(self):
        return Project.visible_objects.all()

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
            status.HTTP_200_OK: ProjectStatusSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    def patch(self, request, *args, **kwargs):
        """Updates project status."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = self.get_queryset().get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        old_project_status = project.project_status
        new_project_status = request.data["project_status"]

        authorized_statuses = []
        if request.user.has_perm("projects.change_project_as_bearer"):
            authorized_statuses += Project.ProjectStatus.get_bearer_project_statuses()
        if request.user.has_perm("projects.change_project_as_validator"):
            authorized_statuses += (
                Project.ProjectStatus.get_validator_project_statuses()
            )
        if new_project_status not in authorized_statuses:
            return response.Response(
                {"error": _("Choosing this status is not allowed.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        statuses_order = Project.ProjectStatus.get_project_statuses_order()
        if old_project_status in Project.ProjectStatus.get_archived_project_statuses():
            return response.Response(
                {"error": _("Cannot change this project status anymore.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif (
            statuses_order[new_project_status] == statuses_order[old_project_status] - 1
            and old_project_status
            not in Project.ProjectStatus.get_rollbackable_project_statuses()
        ):
            return response.Response(
                {"error": _("Cannot rollback to a previous status.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif (
            statuses_order[new_project_status] != statuses_order[old_project_status] + 1
            and statuses_order[new_project_status]
            != statuses_order[old_project_status] - 1
        ):
            return response.Response(
                {"error": _("Wrong status process.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            new_project_status
            in Project.ProjectStatus.get_manageable_project_statuses()
        ):
            document_process_type = ""
            association_email_template_code = ""
            user_email_template_code = ""
            if new_project_status == "PROJECT_PROCESSING":
                document_process_type = "DOCUMENT_PROJECT"
                association_email_template_code = "NEW_ASSOCIATION_PROJECT_TO_PROCESS"
                user_email_template_code = "NEW_USER_PROJECT_TO_PROCESS"
            elif new_project_status == "PROJECT_REVIEW_PROCESSING":
                document_process_type = "DOCUMENT_PROJECT_REVIEW"
                association_email_template_code = (
                    "NEW_ASSOCIATION_PROJECT_REVIEW_TO_PROCESS"
                )
                user_email_template_code = "NEW_USER_PROJECT_REVIEW_TO_PROCESS"
            missing_documents_names = (
                Document.objects.filter(
                    process_type=document_process_type, is_required_in_process=True
                )
                .exclude(
                    id__in=DocumentUpload.objects.filter(
                        project_id=project.id,
                    ).values_list("document_id")
                )
                .values_list("name", flat=True)
            )
            if missing_documents_names.count() > 0:
                missing_documents_names_string = ', '.join(
                    str(item) for item in missing_documents_names
                )
                return response.Response(
                    {
                        "error": _(
                            f"Missing documents : {missing_documents_names_string}."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

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
                funds_misc_used = Fund.objects.filter(
                    id__in=Commission.objects.filter(
                        id__in=ProjectCommissionDate.objects.filter(
                            project_id=project.id
                        ).values_list("commission_date_id")
                    ).values_list("commission_id"),
                    is_site=False,
                )
                context["association_name"] = association.name
                template = MailTemplate.objects.get(
                    code=association_email_template_code
                )
                managers_emails += (
                    institution.default_institution_managers().values_list(
                        "email", flat=True
                    )
                )
                if funds_misc_used.count() > 0:
                    for user_to_check in User.objects.filter(
                        is_superuser=False, is_staff=True
                    ):
                        if user_to_check.has_perm("users.change_user_misc"):
                            managers_emails.append(user_to_check.email)
            elif project.user_id is not None:
                context["first_name"] = request.user.first_name
                context["last_name"] = request.user.last_name
                template = MailTemplate.objects.get(code=user_email_template_code)
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
        return self.update(request, *args, **kwargs)
