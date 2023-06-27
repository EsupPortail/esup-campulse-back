"""Views linked to project commission funds links."""
import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models import Commission, CommissionFund, Fund
from plana.apps.contents.models import Content
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund
from plana.apps.projects.serializers.project_commission_fund import (
    ProjectCommissionFundDataSerializer,
    ProjectCommissionFundSerializer,
)
from plana.apps.users.models.user import AssociationUser, User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import create_pdf, send_mail


class ProjectCommissionFundListCreate(generics.ListCreateAPIView):
    """/projects/commission_funds route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectCommissionFund.objects.all()
    serializer_class = ProjectCommissionFundSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "project_id",
                OpenApiTypes.NUMBER,
                OpenApiParameter.QUERY,
                description="Project id.",
            ),
            OpenApiParameter(
                "commission_id",
                OpenApiTypes.NUMBER,
                OpenApiParameter.QUERY,
                description="Commission id.",
            ),
        ],
        responses={
            status.HTTP_200_OK: ProjectCommissionFundSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
        },
        tags=["projects/commission_funds"],
    )
    def get(self, request, *args, **kwargs):
        """Lists all commission funds that can be linked to a project."""
        project_id = request.query_params.get("project_id")
        commission_id = request.query_params.get("commission_id")

        if not request.user.has_perm(
            "projects.view_projectcommissionfund_any_commission"
        ):
            managed_funds = request.user.get_user_managed_funds()
            if managed_funds.count() > 0:
                user_funds_ids = managed_funds
            else:
                user_funds_ids = request.user.get_user_funds()
        else:
            user_funds_ids = Fund.objects.all().values_list("id")
        if not request.user.has_perm(
            "projects.view_projectcommissionfund_any_institution"
        ):
            user_institutions_ids = request.user.get_user_managed_institutions()
        else:
            user_institutions_ids = Institution.objects.all().values_list("id")

        if not request.user.has_perm(
            "projects.view_projectcommissionfund_any_commission"
        ) or not request.user.has_perm(
            "projects.view_projectcommissionfund_any_institution"
        ):
            user_associations_ids = request.user.get_user_associations()
            user_projects_ids = Project.visible_objects.filter(
                models.Q(user_id=request.user.pk)
                | models.Q(association_id__in=user_associations_ids)
            ).values_list("id")

            self.queryset = self.queryset.filter(
                models.Q(project_id__in=user_projects_ids)
                | models.Q(
                    commission_fund_id__in=CommissionFund.objects.filter(
                        fund_id__in=user_funds_ids
                    ).values_list("id")
                )
                | models.Q(
                    project_id__in=(
                        Project.visible_objects.filter(
                            association_id__in=Association.objects.filter(
                                institution_id__in=user_institutions_ids
                            ).values_list("id")
                        ).values_list("id")
                    )
                )
            )

        if project_id:
            self.queryset = self.queryset.filter(project_id=project_id)

        if commission_id:
            commission_funds_ids = CommissionFund.objects.filter(
                commission_id=commission_id
            ).values_list("id")
            self.queryset = self.queryset.filter(
                commission_fund_id__in=commission_funds_ids
            )

        return self.list(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_201_CREATED: ProjectCommissionFundSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/commission_funds"],
    )
    def post(self, request, *args, **kwargs):
        """Creates a link between a project and a commission fund object."""
        try:
            project = Project.visible_objects.get(id=request.data["project"])
            commission_fund = CommissionFund.objects.get(
                id=request.data["commission_fund"]
            )
            fund = Fund.objects.get(id=commission_fund.fund_id)
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project or commission date does not exist.")},
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

        if not request.user.can_edit_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        validator_fields = [
            "amount_earned",
            "is_validated_by_admin",
        ]
        if not request.user.has_perm(
            "project.change_projectcommissionfund_as_validator"
        ):
            for validator_field in validator_fields:
                if (
                    validator_field in request.data
                    and request.data[validator_field] is not None
                ):
                    return response.Response(
                        {
                            "error": _(
                                "Not allowed to update validator fields for this project's commission fund."
                            )
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

        if fund.is_site is True and (
            project.user_id is not None
            or (
                project.association_id is not None
                and Association.objects.get(id=project.association_id).is_site is False
            )
        ):
            return response.Response(
                {"error": _("Not allowed to submit a project to this commission.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        commission = Commission.objects.get(id=commission_fund.commission_id)

        if commission.submission_date < datetime.date.today():
            return response.Response(
                {"error": _("Submission date for this commission is gone.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not commission.is_open_to_projects:
            return response.Response(
                {"error": _("This commission is not accepting submissions for now.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pcf = ProjectCommissionFund.objects.filter(
            project_id=request.data["project"],
            commission_fund_id=request.data["commission_fund"],
        ).count()
        if pcf > 0:
            return response.Response(
                {
                    "error": _(
                        "This project is already submitted to this commission fund."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        commission_funds = CommissionFund.objects.filter(
            id__in=ProjectCommissionFund.objects.filter(
                project_id=project.id
            ).values_list("commission_fund_id")
        )
        for commission_fund in commission_funds:
            if commission_fund.commission_id != commission.id:
                return response.Response(
                    {"error": _("Cannot submit a project to multiple commissions.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        project.edition_date = datetime.date.today()
        project.save()

        return super().create(request, *args, **kwargs)


class ProjectCommissionFundRetrieve(generics.RetrieveAPIView):
    """/projects/{project_id}/commission_funds route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectCommissionFund.objects.all()
    serializer_class = ProjectCommissionFundSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: ProjectCommissionFundSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/commission_funds"],
    )
    def get(self, request, *args, **kwargs):
        """Retrieves all commission dates linked to a project."""
        try:
            project = Project.visible_objects.get(id=kwargs["project_id"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            not request.user.has_perm(
                "projects.view_projectcommissionfund_any_commission"
            )
            and not request.user.has_perm(
                "projects.view_projectcommissionfund_any_institution"
            )
            and not request.user.can_access_project(project)
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this project commission funds.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(
            self.queryset.filter(project_id=kwargs["project_id"]), many=True
        )
        return response.Response(serializer.data)


class ProjectCommissionFundUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """/projects/{project_id}/commission_funds/{commission_fund_id} route"""

    queryset = ProjectCommissionFund.objects.all()
    serializer_class = ProjectCommissionFundDataSerializer

    def get_permissions(self):
        if self.request.method in ("GET", "PUT"):
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

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
        parameters=[
            OpenApiParameter(
                "new_commission_fund_id",
                OpenApiTypes.NUMBER,
                OpenApiParameter.QUERY,
                description="New Commission Fund ID.",
            ),
        ],
        responses={
            status.HTTP_200_OK: ProjectCommissionFundDataSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/commission_funds"],
    )
    def patch(self, request, *args, **kwargs):
        """Updates details of a project linked to a commission fund object."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = Project.objects.get(id=kwargs["project_id"])
            project_commission_fund = ProjectCommissionFund.objects.get(
                project_id=kwargs["project_id"],
                commission_fund_id=kwargs["commission_fund_id"],
            )
            commission_fund = CommissionFund.objects.get(
                id=kwargs["commission_fund_id"]
            )
            commission = Commission.objects.get(id=commission_fund.commission_id)
            fund = Fund.objects.get(id=commission_fund.fund_id)
        except ObjectDoesNotExist:
            return response.Response(
                {
                    "error": _(
                        "Link between this project and commission does not exist."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.can_edit_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        bearer_fields = [
            "is_first_edition",
            "amount_asked_previous_edition",
            "amount_earned_previous_edition",
            "amount_asked",
        ]
        if not request.user.has_perm("project.change_projectcommissionfund_as_bearer"):
            for bearer_field in bearer_fields:
                if (
                    bearer_field in request.data
                    and request.data[bearer_field] is not None
                ):
                    return response.Response(
                        {
                            "error": _(
                                "Not allowed to update bearer fields for this project's commission."
                            )
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

        validator_fields = [
            "amount_earned",
            "is_validated_by_admin",
            "commission_fund_id",
            "project_id",
        ]
        if not request.user.has_perm(
            "project.change_projectcommissionfund_as_validator"
        ):
            for validator_field in validator_fields:
                if (
                    validator_field in request.data
                    and request.data[validator_field] is not None
                ):
                    return response.Response(
                        {
                            "error": _(
                                "Not allowed to update validator fields for this project's commission."
                            )
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

        if commission.submission_date < datetime.date.today():
            return response.Response(
                {"error": _("Submission date for this commission is gone.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_site = get_current_site(request)
        context = {
            "site_domain": current_site.domain,
            "site_name": current_site.name,
        }
        email = ""
        if project.association_id is not None:
            email = User.objects.get(
                id=AssociationUser.objects.get(id=project.association_user_id).user_id
            ).email
        elif project.user_id is not None:
            email = User.objects.get(id=project.user_id).email

        if "new_commission_fund_id" in request.data:
            try:
                new_commission_fund = CommissionFund.objects.get(
                    id=request.data["new_commission_fund_id"]
                )
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("New Commission Fund does not exist.")},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if commission_fund.fund_id != new_commission_fund.fund_id:
                return response.Response(
                    {
                        "error": _(
                            "New Commission Fund is not linked to the same fund that the old one."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if commission_fund.commission_date >= new_commission_fund.commission_date:
                return response.Response(
                    {
                        "error": _(
                            "New Commission Fund is linked to an older commission that the old one."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            template = MailTemplate.objects.get(code="PROJECT_REPORTED")
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=email,
                subject=template.subject.replace(
                    "{{ site_name }}", context["site_name"]
                ),
                message=template.parse_vars(request.user, request, context),
            )

        # TODO : add other templates and contexts
        if "amount_earned" in request.data:
            if request.data["amount_earned"] == 0:
                template = MailTemplate.objects.get(code="PROJECT_FUND_REFUSED")
            else:
                template = MailTemplate.objects.get(code="PROJECT_FUND_ATTRIBUTED")
                # Creating context for notifications attachments
                attach_template_name = settings.TEMPLATES_NOTIFICATIONS[
                    f"NOTIFICATION_{fund.acronym.upper()}_ATTRIBUTION"
                ]
                context_attach = {
                    "amount_earned": request.data["amount_earned"],
                    "project_name": project.name,
                    "date": datetime.datetime.now(),
                    "content": Content.objects.get(
                        code=f"NOTIFICATION_{fund.acronym.upper()}_ATTRIBUTION"
                    ),
                }
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=email,
                subject=template.subject.replace(
                    "{{ site_name }}", context["site_name"]
                ),
                message=template.parse_vars(request.user, request, context),
                attach_custom={
                    "filename": "test.pdf",
                    "context_attach": context_attach,
                    "mimetype": "application/pdf",
                    "request": request,
                    "template_name": attach_template_name,
                },
            )

        for field in request.data:
            setattr(project_commission_fund, field, request.data[field])
        project_commission_fund.save()

        remaining_project_commission_funds_count = ProjectCommissionFund.objects.filter(
            project_id=project.id, amount_earned__isnull=True
        ).count()
        if remaining_project_commission_funds_count == 0:
            project.project_status = "PROJECT_REVIEW_DRAFT"
            project.save()

        unvalidated_project_commission_funds_count = (
            ProjectCommissionFund.objects.filter(
                project_id=project.id, is_validated_by_admin=False
            ).count()
        )
        if (
            "is_validated_by_admin" in request.data
            and request.data["is_validated_by_admin"] is True
            and project.project_status == "PROJECT_PROCESSING"
            and unvalidated_project_commission_funds_count == 0
        ):
            project.project_status = "PROJECT_VALIDATED"
            project.save()
            template = MailTemplate.objects.get(code="PROJECT_VALIDATED")
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=email,
                subject=template.subject.replace(
                    "{{ site_name }}", context["site_name"]
                ),
                message=template.parse_vars(request.user, request, context),
            )

        return response.Response({}, status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            status.HTTP_204_NO_CONTENT: ProjectCommissionFundSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
        tags=["projects/commission_funds"],
    )
    def delete(self, request, *args, **kwargs):
        """Destroys details of a project linked to a commission date."""
        try:
            project = Project.visible_objects.get(id=kwargs["project_id"])
            project_commission_fund = ProjectCommissionFund.objects.get(
                project_id=kwargs["project_id"],
                commission_fund_id=kwargs["commission_fund_id"],
            )
        except ObjectDoesNotExist:
            return response.Response(
                {
                    "error": _(
                        "Link between this project and commission does not exist."
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.can_edit_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        project.edition_date = datetime.date.today()
        project.save()
        project_commission_fund.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
