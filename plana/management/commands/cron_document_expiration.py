import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.translation import gettext as _

from plana.apps.associations.models.association import Association
from plana.apps.contents.models.setting import Setting
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
                document_id__in=Document.objects.filter(
                    Q(days_before_expiration__isnull=False) ^ Q(expiration_day__isnull=False)
                ).values_list("id")
            )
            for document_upload in document_uploads_with_expiration:
                document = Document.objects.get(id=document_upload.document_id)
                expiration_date = None
                if document_upload.validated_date is not None:
                    if document.expiration_day is not None:
                        if document.expiration_day <= document_upload.validated_date.strftime("%m-%d"):
                            expiration_date = datetime.datetime.strptime(
                                f"{document_upload.validated_date.year + 1}-{document.expiration_day}",
                                "%Y-%m-%d",
                            ).date()
                        expiration_date = datetime.datetime.strptime(
                            f"{document_upload.validated_date.year}-{document.expiration_day}",
                            "%Y-%m-%d",
                        ).date()
                    if document.days_before_expiration is not None:
                        expiration_date = document_upload.validated_date + document.days_before_expiration
                if expiration_date is not None and datetime.date.today() == expiration_date - datetime.timedelta(
                    days=Setting.objects.get(setting="CRON_DAYS_BEFORE_DOCUMENT_EXPIRATION_WARNING").parameters[
                        "value"
                    ]
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
                elif expiration_date is not None and datetime.date.today() == expiration_date:
                    document_upload.delete()

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
