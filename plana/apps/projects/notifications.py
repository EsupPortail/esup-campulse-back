"""Utils file for projects app, mainly used for notifications handling"""
import datetime
import logging
from typing import Optional

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.formats import date_format

from plana.apps.commissions.models import Commission, Fund
from plana.apps.contents.models import Content
from plana.apps.history.models import History
from plana.apps.projects.models import ProjectCommissionFund, ProjectComment, Project
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail

logger = logging.getLogger(__name__)


def build_pcf_notification_attachment_data(request, pcf: ProjectCommissionFund, template_path: str, content_code: str, from_admin: bool) -> Optional[dict]:
    """Builds required data for a pcf notification pdf attachment, only if a template path is provided"""
    if not template_path:
        return

    today = datetime.date.today()
    project = pcf.project
    owner_data = project.get_project_owner_data()
    # Retrieving content linked to the template path
    content = Content.objects.get(code=content_code)
    # Retrieving last comment of the project or None
    comment = ProjectComment.objects.filter(project=project, is_visible=True).order_by("-creation_date").values_list("text", flat=True).first() or ""

    attachment = {
        "template_name": f"{settings.S3_PDF_FILEPATH}/{settings.TEMPLATES_PDF_NOTIFICATIONS_FOLDER}/{template_path}",
        "filename": f"{content.title}.pdf",
        "context_attach": {
            "amount_earned": pcf.amount_earned,
            "project_name": project.name,
            "project_manual_identifier": project.manual_identifier,
            "date": date_format(today, format="d F Y", use_l10n=True),  # Uses request locale for month translation
            "year": today.strftime('%Y'),
            "date_commission": date_format(pcf.commission_fund.commission.commission_date, format="d F Y", use_l10n=True),
            "owner": owner_data,
            "content": content,
            "comment": comment,
        },
        "mimetype": "application/pdf",
        "request": request
    }
    # If from admin, must not override current pcf.last_notification_file (defined by pcf_obj in send_mail)
    if not from_admin:
        attachment["pcf_obj"] = pcf

    return attachment


def send_pcf_notification_mail_with_attachments(request, pcf: ProjectCommissionFund, notification_type: str, from_admin: bool = False) -> None:
    """
    Sends correct email with correct generated pdf notification attachments depending on notification type
    Also used for pdf templates test purposes in django admin with param 'from_admin'
    """
    # Initializing data
    project = pcf.project
    fund = pcf.commission_fund.fund
    current_site = get_current_site(request)
    context = {
        "site_domain": current_site.domain,
        "site_name": current_site.name,
        "project_name": project.name,
        "fund_name": fund.name,
    }

    # If wrong given notification type do nothing
    if not notification_type or notification_type not in ["ATTRIBUTION", "REJECTION", "POSTPONE"]:
        return

    # Each type of action triggers a different email with different notification templates
    code_templates = {
        "ATTRIBUTION": (
            "USER_OR_ASSOCIATION_PROJECT_FUND_CONFIRMATION",
            [
                (fund.attribution_template_path, f"NOTIFICATION_{fund.acronym.upper()}_ATTRIBUTION"),
                (fund.decision_attribution_template_path, f"NOTIFICATION_{fund.acronym.upper()}_DECISION_ATTRIBUTION")
            ],
        ),
        "REJECTION": (
            "USER_OR_ASSOCIATION_PROJECT_FUND_REJECTION",
            [(fund.rejection_template_path, f"NOTIFICATION_{fund.acronym.upper()}_REJECTION")],
        ),
        "POSTPONE": (
            "USER_OR_ASSOCIATION_PROJECT_POSTPONED",
            [(fund.postpone_template_path, f"NOTIFICATION_{fund.acronym.upper()}_POSTPONE")],
        ),
    }
    mail_code, pdf_configs = code_templates.get(notification_type, ("", []))

    # Generate attachments
    attachments = []
    for template_path, template_name in pdf_configs:
        if attachment := build_pcf_notification_attachment_data(
            request=request,
            pcf=pcf,
            template_path=template_path,
            content_code=template_name,
            from_admin=from_admin
        ):
            attachments.append(attachment)

    # If request is sent from admin, send mail to request user only (used for testing purposes)
    cc = []
    to = request.user.email if from_admin else project.get_project_owner_data().get("email")
    # postpone notifications does not need to be sent to managers
    if not from_admin and notification_type != "POSTPONE":
        cc = project.get_project_default_manager_emails(fund.id)

    # Send the final email with correct generated attachments
    mail_template = MailTemplate.objects.get(code=mail_code)
    send_mail(
        from_=settings.DEFAULT_FROM_EMAIL,
        to_=to,
        cc_=cc,
        subject=mail_template.subject.replace("{{ site_name }}", context["site_name"]),
        message=mail_template.parse_vars(request.user, request, context),
        temp_attachments=attachments,
    )


def send_project_status_update_notification(request, project_obj: Project) -> None:
    """Used to send notifications on main project status update (commission related), from bearer or manager"""

    def _get_bearer_context(project):
        if project.project_status in Project.ProjectStatus.get_email_project_processing_project_statuses():
            prefix = "MANAGER_PROJECT"
        elif project.project_status in Project.ProjectStatus.get_email_review_processing_project_statuses():
            prefix = "MANAGER_PROJECT_REVIEW"
        else:
            return {}

        role = "ASSOCIATION" if project.association_id else "USER" if project.user_id else None
        if not role:
            return {}

        # Commission should be mandatory at this state
        commission = Commission.objects.filter(commissionfund__projectcommissionfund__project=project).first()
        bearer_context = {
            "template_code": f"{prefix}_{role}_CREATION",
            "commission_name": commission.name,
            "project_name": project.name,
            "to": project.get_project_default_manager_emails()
        }
        owner_data = project.get_project_owner_data()
        if project.association_id:
            bearer_context["association_name"] = owner_data.get("name")
        elif project.user_id:
            bearer_context["first_name"] = owner_data.get("first_name")
            bearer_context["last_name"] = owner_data.get("last_name")

        return bearer_context

    def _get_validator_context(project):
        mail_templates_codes_by_status = {
            "PROJECT_DRAFT_PROCESSED": "USER_OR_ASSOCIATION_PROJECT_NEEDS_CHANGES",
            "PROJECT_REJECTED": "USER_OR_ASSOCIATION_PROJECT_REJECTION",
            "PROJECT_VALIDATED": "USER_OR_ASSOCIATION_PROJECT_CONFIRMATION",
            "PROJECT_REVIEW_DRAFT": "USER_OR_ASSOCIATION_PROJECT_NEEDS_REVIEW",
            "PROJECT_REVIEW_VALIDATED": "USER_OR_ASSOCIATION_PROJECT_REVIEW_CONFIRMATION",
            "PROJECT_CANCELED": "USER_OR_ASSOCIATION_PROJECT_CANCELLATION",
        }
        if not (template_code := mail_templates_codes_by_status.get(project.project_status)):
            return {}
        validator_context = {
            "template_code": template_code,
            "to": project.get_project_owner_data().get("email"),
            "manager_email_address": ','.join(project.get_project_default_manager_emails())
        }
        if project.project_status == "PROJECT_VALIDATED":
            # TODO : Better history model
            History.objects.create(
                action_title="PROJECT_VALIDATED", action_user_id=request.user.pk, project_id=project.id
            )
            commission = Commission.objects.filter(commissionfund__projectcommissionfund__project=project).first()
            fund = Fund.objects.filter(commissionfund__projectcommissionfund__project=project).first()
            validator_context.update({
                "project_name": project.name,
                "fund_name": fund.acronym,
                "commission_name": commission.name
            })
        return validator_context

    if project_obj.project_status in Project.ProjectStatus.get_bearer_project_statuses():
        context = _get_bearer_context(project_obj)
    elif project_obj.project_status in Project.ProjectStatus.get_validator_project_statuses():
        context = _get_validator_context(project_obj)
    else:
        return

    # Mail sending is not mandatory for this workflow step, should not be blocking the process
    try:
        current_site = get_current_site(request)
        context.update({"site_domain": current_site.domain, "site_name": current_site.name})
        template = MailTemplate.objects.get(code=context["template_code"])
        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=context["to"],
            subject=template.subject.replace("{{ site_name }}", context["site_name"]),
            message=template.parse_vars(request.user, request, context),
        )
    except Exception:
        logger.exception(
            "Failed to send status update notification for project %s (status=%s)",
            project_obj.pk,
            project_obj.project_status
        )
