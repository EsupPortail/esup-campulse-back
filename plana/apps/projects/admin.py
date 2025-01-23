"""Admin view for Project models."""
import datetime
from django.conf import settings
from django.contrib import admin
from django.contrib.sites.shortcuts import get_current_site
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from plana.apps.users.models.user import AssociationUser, User

from .models import (
    Category,
    Project,
    ProjectCategory,
    ProjectComment,
    ProjectCommissionFund,
)
from ..contents.models import Content
from ...libs.mail_template.models import MailTemplate
from ...utils import send_mail


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """List view for categories."""

    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """List view for projects."""

    list_display = [
        "name",
        "manual_identifier",
        "user",
        "association",
        "get_association_user",
        "project_status",
        "get_commission_funds",
    ]
    search_fields = [
        "name",
        "manual_identifier",
        "user__first_name",
        "user__last_name",
        "association__acronym",
        "association__name",
        "association_user__user__first_name",
        "association_user__user__last_name",
        "project_status",
    ]

    @admin.display(description=_("Association User"))
    @admin.display(ordering="association_user")
    def get_association_user(self, obj):
        """Get user that manages a project in an association."""
        if obj.association_user is not None:
            user = User.objects.get(id=AssociationUser.objects.get(id=obj.association_user.id).user_id)
            return f"{user.first_name} {user.last_name}"
        return "-"

    @admin.display(description=_("Project commission fund"))
    @admin.display(ordering="projectcommissionfund")
    def get_commission_funds(self, obj):
        """Get commissions and funds linked to a project."""
        project_commission_funds = ProjectCommissionFund.objects.filter(project_id=obj.id)
        if project_commission_funds.count() > 0:
            commission_name = project_commission_funds.first().commission_fund.commission.name
            fund_names = list(project_commission_funds.values_list("commission_fund__fund__acronym", flat=True))
            return f"{commission_name} - {', '.join(fund_names)}"
        return "-"


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    """List view for project categories."""

    list_display = ["category", "project"]
    search_fields = ["category__name", "project__name"]


@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    """List view for project comments."""

    list_display = ["text", "is_visible", "project", "user"]
    list_filter = ["is_visible"]
    search_fields = ["text", "project__name", "user__first_name", "user__last_name"]


class GeneratePDFAction:
    def __init__(self, template_name, description):
        self.template_name = template_name
        self.short_description = description

    @property
    def __name__(self):
        return f"generate_pdf_{self.template_name}"

    # TODO : Add info and error messages
    def __call__(self, modeladmin, request, queryset):
        attachments = []
        for obj in queryset:
            # Retrieving data from ProjectCommissionFund object
            fund = obj.commission_fund.fund
            project = obj.project
            commission = obj.commission_fund.commission
            print(f"NOTIFICATION_{fund.acronym.upper()}_{self.template_name}")
            content = Content.objects.get(code=f"NOTIFICATION_{fund.acronym.upper()}_{self.template_name}")
            owner = {
                "name": "PRENOM NOM",
                "address": "1 Rue du Test STRASBOURG - 67000, FRANCE",
            }
            # Initializing data for PDF attachment
            attachments.append(
                {
                    "template_name": f"{settings.S3_PDF_FILEPATH}/{settings.TEMPLATES_PDF_NOTIFICATIONS_FOLDER}/{getattr(fund, f'{self.template_name.lower()}_template_path')}",
                    "filename": f"{slugify(content.title)}.pdf",
                    "context_attach": {
                        "amount_earned": obj.amount_earned,
                        "project_name": project.name,
                        "project_manual_identifier": project.manual_identifier,
                        "date": datetime.date.today().strftime('%d %B %Y'),
                        "year": datetime.date.today().strftime('%Y'),
                        "date_commission": commission.commission_date.strftime('%d %B %Y'),
                        "owner": owner,
                        "content": content,
                    },
                    "mimetype": "application/pdf",
                    "request": request,
                }

            )

        # Setting up data to send email
        current_site = get_current_site(request)
        context = {
            "site_domain": f"https://{current_site.domain}",
            "site_name": current_site.name,
        }

        code_templates = {
            "ATTRIBUTION": "FUND_CONFIRMATION",
            "REJECTION": "FUND_REJECTION",
            "POSTPONE": "POSTPONED",
            "DECISION_ATTRIBUTION": "FUND_CONFIRMATION",
        }
        template = MailTemplate.objects.get(code=f"USER_OR_ASSOCIATION_PROJECT_{code_templates[self.template_name]}")
        # Send email with all generated PDF attachments
        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=request.user.email,
            subject=template.subject.replace("{{ site_name }}", context["site_name"]),
            message=template.parse_vars(request.user, request, context),
            temp_attachments=attachments,
        )


# Defining PDF actions for ProjectCommissionFund admin
# TODO : limit to test and preprod envs
generate_pdf_attribution = GeneratePDFAction("ATTRIBUTION", "Générer une notification d'attribution")
generate_pdf_rejection = GeneratePDFAction("REJECTION", "Générer une notification de rejet")
generate_pdf_postpone = GeneratePDFAction("POSTPONE", "Générer une notification de report")
generate_pdf_decision_attribution = GeneratePDFAction("DECISION_ATTRIBUTION", "Générer une notification de décision d'attribution")


@admin.register(ProjectCommissionFund)
class ProjectCommissionFundAdmin(admin.ModelAdmin):
    """List view for project commission funds."""
    actions = [
        generate_pdf_attribution,
        generate_pdf_rejection,
        generate_pdf_postpone,
        generate_pdf_decision_attribution,
    ]

    list_display = ["project", "commission_fund", "is_validated_by_admin"]
    list_filter = ["is_validated_by_admin"]
    search_fields = [
        "project__name",
        "commission_fund__commission__name",
        "commission_fund__fund__acronym",
        "commission_fund__fund__name",
    ]
