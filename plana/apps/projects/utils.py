"""Utils file for projects app"""
import datetime
from typing import Optional

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.formats import date_format

from plana.apps.contents.models import Content
from plana.apps.projects.models import ProjectCommissionFund, ProjectComment
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


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
    comment = ProjectComment.objects.filter(project=project).order_by("-creation_date").values_list("text", flat=True).first() or ""

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
