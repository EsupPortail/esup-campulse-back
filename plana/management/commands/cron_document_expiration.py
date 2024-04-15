import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from plana.apps.associations.models.association import Association
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.users.models.user import User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class Command(BaseCommand):
    help = _("Checks statuses of documents uploads.")

    def handle(self, *args, **options):
        try:
            document_uploads_with_expiration = DocumentUpload.objects.filter(
                document_id__in=Document.objects.filter(days_before_expiration__isnull=False).values_list("id")
            )
            for document_upload in document_uploads_with_expiration:
                document = Document.objects.get(id=document_upload.document_id)
                if (
                    document_upload.validated_date is not None
                    and document.days_before_expiration is not None
                    and datetime.date.today()
                    == document_upload.validated_date
                    + document.days_before_expiration
                    - datetime.timedelta(days=int(settings.CRON_DAYS_BEFORE_DOCUMENT_EXPIRATION_WARNING))
                ) or (
                    document_upload.validated_date is not None
                    and document.expiration_day is not None
                    and datetime.date.today()
                    == datetime.datetime.strptime(document.expiration_day, "%m-%d").date()
                    - datetime.timedelta(days=int(settings.CRON_DAYS_BEFORE_DOCUMENT_EXPIRATION_WARNING))
                ):
                    template = MailTemplate.objects.get(
                        code="USER_OR_ASSOCIATION_DOCUMENT_EXPIRATION_WARNING_SCHEDULED"
                    )
                    current_site = get_current_site(None)
                    context = {"site_name": current_site.name}
                    email = ""
                    if document_upload.user_id is not None:
                        email = User.objects.get(id=document_upload.user_id).email
                    elif document_upload.association_id is not None:
                        email = Association.objects.get(id=document_upload.association_id).email
                    send_mail(
                        from_=settings.DEFAULT_FROM_EMAIL,
                        to_=email,
                        subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                        message=template.parse_vars(None, None, context),
                    )
                elif (
                    document_upload.validated_date is not None
                    and document.days_before_expiration is not None
                    and datetime.date.today() == document_upload.validated_date + document.days_before_expiration
                ) or (
                    document_upload.validated_date is not None
                    and document.expiration_day is not None
                    and datetime.date.today().strftime("%m-%d") == document.expiration_day
                ):
                    document_upload.delete()

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
