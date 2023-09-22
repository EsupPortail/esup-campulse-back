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
from plana.apps.commissions.models import Commission, CommissionFund, Fund
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_comment import ProjectComment
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund
from plana.apps.projects.serializers.project import (
    ProjectPartialDataSerializer,
    ProjectSerializer,
    ProjectStatusSerializer,
    ProjectUpdateManagerSerializer,
    ProjectUpdateSerializer,
)
from plana.apps.users.models.user import AssociationUser, User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail, to_bool


class ProjectListCreate(generics.ListCreateAPIView):
    """/projects/ route."""

    filter_backends = [filters.SearchFilter]
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    search_fields = [
        "name__nospaces__unaccent",
        "creation_date__year",
        "manual_identifier",
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
                "manual_identifier",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by manual identifier.",
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
                "commission_id",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by Commission ID linked to a project.",
            ),
            OpenApiParameter(
                "project_statuses",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Filter by Project Statuses codes.",
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
        """List all projects linked to a user, or all projects with all their details (manager)."""
        queryset = self.get_queryset()

        name = request.query_params.get("name")
        year = request.query_params.get("year")
        manual_identifier = request.query_params.get("manual_identifier")
        user = request.query_params.get("user_id")
        association = request.query_params.get("association_id")
        commission = request.query_params.get("commission_id")
        project_statuses = request.query_params.get("project_statuses")
        with_comments = request.query_params.get("with_comments")
        active_projects = request.query_params.get("active_projects")

        if name is not None and name != "":
            name = str(name).strip()
            queryset = queryset.filter(name__nospaces__unaccent__icontains=name.replace(" ", ""))

        if year is not None and year != "":
            queryset = queryset.filter(creation_date__year=year)

        if manual_identifier is not None and manual_identifier != "":
            manual_identifier = str(manual_identifier).strip()
            queryset = queryset.filter(
                manual_identifier__nospaces__unaccent__icontains=manual_identifier.replace(" ", "")
            )

        if not request.user.has_perm("projects.view_project_any_fund"):
            managed_funds = request.user.get_user_managed_funds()
            if managed_funds.count() > 0:
                user_funds_ids = managed_funds
            else:
                user_funds_ids = request.user.get_user_funds()
        else:
            user_funds_ids = Fund.objects.all().values_list("id")

        if not request.user.has_perm("projects.view_project_any_institution"):
            user_institutions_ids = request.user.get_user_managed_institutions()
        else:
            user_institutions_ids = Institution.objects.all().values_list("id")

        if not request.user.has_perm("projects.view_project_any_fund") or not request.user.has_perm(
            "projects.view_project_any_institution"
        ):
            user_associations_ids = request.user.get_user_associations()
            user_projects_ids = Project.visible_objects.filter(
                models.Q(user_id=request.user.pk) | models.Q(association_id__in=user_associations_ids)
            ).values_list("id")
            if not request.user.has_perm("projects.view_project_any_status"):
                queryset = queryset.filter(
                    models.Q(id__in=user_projects_ids)
                    | models.Q(
                        id__in=(
                            ProjectCommissionFund.objects.filter(
                                commission_fund_id__in=CommissionFund.objects.filter(
                                    fund_id__in=user_funds_ids
                                ).values_list("id")
                            ).values_list("project_id")
                        ),
                        project_status__in=Project.ProjectStatus.get_commissionnable_project_statuses(),
                    )
                    | models.Q(
                        association_id__in=Association.objects.filter(
                            institution_id__in=user_institutions_ids
                        ).values_list("id")
                    )
                )
            else:
                queryset = queryset.filter(
                    models.Q(id__in=user_projects_ids)
                    | models.Q(
                        id__in=(
                            ProjectCommissionFund.objects.filter(
                                commission_fund_id__in=CommissionFund.objects.filter(
                                    fund_id__in=user_funds_ids
                                ).values_list("id")
                            ).values_list("project_id")
                        ),
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
                if project_status_code != "" and project_status_code in all_project_statuses
            ]
            queryset = queryset.filter(project_status__in=project_statuses_codes)

        if commission is not None and commission != "":
            queryset = queryset.filter(
                id__in=ProjectCommissionFund.objects.filter(
                    commission_fund_id__in=CommissionFund.objects.filter(commission_id=commission).values_list("id")
                ).values_list("project_id")
            )

        if with_comments is not None and with_comments != "":
            projects_ids_with_comments = ProjectComment.objects.all().values_list("project_id")
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

        for project in queryset:
            pcf = project.projectcommissionfund_set.first()
            if pcf is not None:
                project.commission = Commission.objects.get(
                    id=CommissionFund.objects.get(id=pcf.commission_fund_id).commission_id
                )
            else:
                project.commission = None

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
        """Create a new project."""
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
                        and not request.user.is_president_in_association(request.data["association"])
                    ) or not request.user.has_perm("projects.add_project_association"):
                        return response.Response(
                            {"error": _("User not allowed to create a new project for this association.")},
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
        ) and ("user" in request.data and request.data["user"] is not None and request.data["user"] != ""):
            return response.Response(
                {"error": _("A project can only have one affectation.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            not "association" in request.data
            or request.data["association"] is None
            or request.data["association"] == ""
        ) and (not "user" in request.data or request.data["user"] is None or request.data["user"] == ""):
            return response.Response(
                {"error": _("Missing affectation of the new project.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            ("user" in request.data and "association_user" in request.data)
            or (not "association" in request.data and "association_user" in request.data)
            or (not "association_user" in request.data and "association" in request.data)
        ):
            return response.Response(
                {"error": _("Cannot add a user from an association.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "association" in request.data and "association_user" in request.data:
            association_user_count = AssociationUser.objects.filter(
                id=request.data["association_user"],
                association_id=request.data["association"],
            ).count()
            if association_user_count == 0:
                return response.Response(
                    {"error": _("Link between association and user does not exist.")},
                    status=status.HTTP_404_NOT_FOUND,
                )

        if (
            "amount_students_audience" in request.data
            and "amount_all_audience" in request.data
            and int(request.data["amount_students_audience"]) > int(request.data["amount_all_audience"])
        ):
            return response.Response(
                {"error": _("Number of students in audience cannot exceed number of all people in audience.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "planned_start_date" in request.data
            and "planned_end_date" in request.data
            and datetime.datetime.strptime(request.data["planned_start_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
            > datetime.datetime.strptime(request.data["planned_end_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        ):
            return response.Response(
                {"error": _("Can't set planned start date after planned end date.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        today = datetime.date.today()
        request.data["creation_date"] = today
        request.data["edition_date"] = today

        return super().create(request, *args, **kwargs)


class ProjectRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/projects/{id} route."""

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
        """Retrieve a project with all its details."""
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

        if (
            not request.user.has_perm("projects.view_project_any_status")
            and (
                (project.association_id is not None and not request.user.is_in_association(project.association_id))
                or (project.user_id is not None and request.user.pk != project.user_id)
            )
            and project.project_status not in Project.ProjectStatus.get_commissionnable_project_statuses()
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
        """Update project details."""
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

        if not request.user.can_edit_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            not request.user.has_perm("projects.change_project_as_validator")
            and project.project_status not in Project.ProjectStatus.get_unfinished_project_statuses()
        ):
            return response.Response(
                {"error": _("Project is not a draft that can be edited.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if "association_user" in request.data and project.user_id is not None:
            return response.Response(
                {"error": _("Cannot add a user from an association.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "association_user" in request.data:
            association_user_count = AssociationUser.objects.filter(
                id=request.data["association_user"],
                association_id=project.association_id,
            ).count()
            if association_user_count == 0:
                return response.Response(
                    {"error": _("Link between association and user does not exist.")},
                    status=status.HTTP_404_NOT_FOUND,
                )

        expired_project_commission_dates_count = ProjectCommissionFund.objects.filter(
            project_id=project.id,
            commission_fund_id__in=Commission.objects.filter(
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
            and int(request.data["amount_students_audience"]) > int(request.data["amount_all_audience"])
        ):
            return response.Response(
                {"error": _("Number of students in audience cannot exceed number of all people in audience.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "planned_start_date" in request.data
            and "planned_end_date" in request.data
            and datetime.datetime.strptime(request.data["planned_start_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
            > datetime.datetime.strptime(request.data["planned_end_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        ):
            return response.Response(
                {"error": _("Can't set planned start date after planned end date.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data["edition_date"] = datetime.date.today()
        return self.partial_update(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: ProjectSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    def delete(self, request, *args, **kwargs):
        """Destroys a project."""
        try:
            project = self.get_queryset().get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.can_edit_project(project):
            return response.Response(
                {"error": _("Not allowed to delete this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if project.project_status not in Project.ProjectStatus.get_unfinished_project_statuses():
            return response.Response(
                {"error": _("Cannot delete a non-draft project.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self.destroy(request, *args, **kwargs)


class ProjectStatusUpdate(generics.UpdateAPIView):
    """/projects/{id}/status route."""

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
        """Update project status."""
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

        if not request.user.can_edit_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        old_project_status = project.project_status
        new_project_status = request.data["project_status"]

        authorized_statuses = []
        if request.user.has_perm("projects.change_project_as_bearer"):
            authorized_statuses += Project.ProjectStatus.get_bearer_project_statuses()
        if request.user.has_perm("projects.change_project_as_validator"):
            authorized_statuses += Project.ProjectStatus.get_validator_project_statuses()
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
        if (
            statuses_order[new_project_status] == statuses_order[old_project_status] - 1
            and old_project_status not in Project.ProjectStatus.get_rollbackable_project_statuses()
        ):
            return response.Response(
                {"error": _("Cannot rollback to a previous status.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if (
            statuses_order[new_project_status] != statuses_order[old_project_status] + 1
            and statuses_order[new_project_status] != statuses_order[old_project_status] - 1
        ):
            return response.Response(
                {"error": _("Wrong status process.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        template = None
        current_site = get_current_site(request)
        context = {
            "site_domain": current_site.domain,
            "site_name": current_site.name,
        }

        if new_project_status in Project.ProjectStatus.get_bearer_project_statuses():
            document_process_types = []
            association_email_template_code = ""
            user_email_template_code = ""
            if new_project_status in Project.ProjectStatus.get_email_project_processing_project_statuses():
                document_process_types = ["DOCUMENT_PROJECT", "CHARTER_PROJECT_FUND"]
                association_email_template_code = "MANAGER_PROJECT_ASSOCIATION_CREATION"
                user_email_template_code = "MANAGER_PROJECT_USER_CREATION"
                request.data["processing_date"] = datetime.datetime.today()
            elif new_project_status in Project.ProjectStatus.get_email_review_processing_project_statuses():
                document_process_types = ["DOCUMENT_PROJECT_REVIEW"]
                association_email_template_code = "MANAGER_PROJECT_REVIEW_ASSOCIATION_CREATION"
                user_email_template_code = "MANAGER_PROJECT_REVIEW_USER_CREATION"
            missing_documents_names = (
                Document.objects.filter(
                    models.Q(process_type__in=document_process_types)
                    & (
                        models.Q(is_required_in_process=True, fund_id=None)
                        | models.Q(
                            is_required_in_process=True,
                            fund_id__in=CommissionFund.objects.filter(
                                id__in=ProjectCommissionFund.objects.filter(project_id=project.id).values_list(
                                    "commission_fund_id"
                                )
                            ).values_list("fund_id"),
                        )
                    )
                )
                .exclude(
                    id__in=DocumentUpload.objects.filter(
                        project_id=project.id,
                    ).values_list("document_id")
                )
                .values_list("name")
            )
            if missing_documents_names.count() > 0:
                missing_documents_names_string = ', '.join(str(item) for item in missing_documents_names)
                return response.Response(
                    {"error": _(f"Missing documents : {missing_documents_names_string}.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if new_project_status in Project.ProjectStatus.get_identifier_project_statuses():
                now = datetime.datetime.now()
                if now.month >= settings.NEW_YEAR_MONTH_INDEX:
                    year = now.year
                else:
                    year = now.year - 1
                projects_year_count = Project.visible_objects.filter(manual_identifier__startswith=year).count()
                project.manual_identifier = f"{year}{projects_year_count+1:04}"
                project.save()

            managers_emails = project.get_project_default_manager_emails()
            if project.association_id is not None:
                association = Association.objects.get(id=project.association_id)
                funds_misc_used = Fund.objects.filter(
                    id__in=CommissionFund.objects.filter(
                        id__in=ProjectCommissionFund.objects.filter(project_id=project.id).values_list(
                            "commission_fund_id"
                        )
                    ).values_list("fund_id"),
                    is_site=False,
                )
                context["association_name"] = association.name
                template = MailTemplate.objects.get(code=association_email_template_code)
                if funds_misc_used.count() > 0:
                    for user_to_check in User.objects.filter(is_superuser=False, is_staff=True):
                        if user_to_check.has_perm("users.change_user_misc"):
                            managers_emails.append(user_to_check.email)
            elif project.user_id is not None:
                context["first_name"] = request.user.first_name
                context["last_name"] = request.user.last_name
                template = MailTemplate.objects.get(code=user_email_template_code)

            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=managers_emails,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(request.user, request, context),
            )
        elif new_project_status in Project.ProjectStatus.get_validator_project_statuses():
            mail_templates_codes_by_status = {
                "PROJECT_DRAFT_PROCESSED": "USER_OR_ASSOCIATION_PROJECT_NEEDS_CHANGES",
                "PROJECT_REJECTED": "USER_OR_ASSOCIATION_PROJECT_REJECTION",
                "PROJECT_VALIDATED": "USER_OR_ASSOCIATION_PROJECT_CONFIRMATION",
                "PROJECT_REVIEW_DRAFT": "USER_OR_ASSOCIATION_PROJECT_NEEDS_REVIEW",
                "PROJECT_REVIEW_VALIDATED": "USER_OR_ASSOCIATION_PROJECT_REVIEW_CONFIRMATION",
                "PROJECT_CANCELED": "USER_OR_ASSOCIATION_PROJECT_CANCELLATION",
            }
            template = MailTemplate.objects.get(code=mail_templates_codes_by_status[new_project_status])
            email = ""
            if project.association_id is not None:
                if project.association_user_id is not None:
                    email = User.objects.get(
                        id=AssociationUser.objects.get(id=project.association_user_id).user_id
                    ).email
                else:
                    email = Association.objects.get(id=project.association_id).email
            elif project.user_id is not None:
                email = User.objects.get(id=project.user_id).email
            context["manager_email_address"] = ','.join(project.get_project_default_manager_emails())
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=email,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(request.user, request, context),
            )

        request.data["edition_date"] = datetime.date.today()
        return self.update(request, *args, **kwargs)
