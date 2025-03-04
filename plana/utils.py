"""Generic functions to send emails, and convert "true" and "false" to real booleans."""

import ast
import datetime
import logging

import boto3
import weasyprint
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.template import Context, Template
from django.template.loader import get_template, render_to_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from zxcvbn import zxcvbn


def check_valid_password(password):
    """Check password standard rules and zxcvbn rules."""
    messages = []

    password_result = zxcvbn(password)
    if password_result["score"] < 4 and len(messages) == 0:
        messages += [_("Password is still too weak, please add some characters.")]
    messages += password_result["feedback"]["suggestions"]

    return_messages = {
        "valid": len(messages) == 0,
        "messages": messages,
    }
    return return_messages


def _listify(x):
    return list(filter(None, set(x if isinstance(x, (list, tuple, set)) else [x])))


def send_mail(
    to_,
    subject,
    message,
    from_='',
    cc_='',
    bcc_='',
    attachments=None,
    temp_attachments=None,
    has_html=True,
    **kwargs,
):
    """Send an email."""
    # Listify recipient address
    to_ = _listify(to_)
    from_ = from_ or settings.DEFAULT_FROM_EMAIL

    mail = EmailMultiAlternatives(subject, message, from_, to_, cc=cc_, bcc=bcc_, **kwargs)
    if has_html:
        mail.attach_alternative(message, "text/html")

    # Attachments for existing files
    attachments = attachments or ()
    for att in attachments:
        with att.storage.open(f'{att.filepath}/{att.filename}', 'rb') as file:
            content = file.read()
            mail.attach(att.filename, content, att.mimetype)

    # Attachments for generated files
    if temp_attachments is not None:
        for temp_attachment in temp_attachments:
            if temp_attachment is not None:
                binary = generate_pdf_binary(
                        temp_attachment["context_attach"],
                        temp_attachment["request"],
                        temp_attachment["template_name"],
                )
                if "pcf_obj" in temp_attachment:
                    temp_attachment["pcf_obj"].last_notification_file.save(
                        f"notification_{temp_attachment['context_attach']['project_name']}.pdf",
                        ContentFile(binary),
                        save=True
                    )
                mail.attach(
                    temp_attachment["filename"],
                    binary,
                    temp_attachment["mimetype"],
                )

    logger = logging.getLogger(__name__)
    try:
        mail.send()
    except Exception as error:
        if settings.DEBUG:
            print(f"Mail \"{subject}\" not sent.")
        else:
            logger.exception(error)
            raise


def to_bool(attr):
    """Translate strings like "true"/"false" into boolean."""
    if isinstance(attr, bool):
        return attr
    if isinstance(attr, str):
        return ast.literal_eval(attr.capitalize())
    return None


def valid_date_format(date):
    """Check date format without time."""
    date_format = "%Y-%m-%d"
    try:
        datetime.datetime.strptime(date, date_format)
    except ValueError:
        return False
    return True


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    )


def generate_pdf_response(filename, dict_data, type_doc, base_url):
    """Generate a PDF file as a HTTP response (used for all PDF exports returned in API routes)."""
    if settings.USE_S3 == True:
        s3 = get_s3_client()
        data = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=settings.TEMPLATES_PDF_FILEPATHS[type_doc])
        template = Template(data['Body'].read().decode('utf-8'))
        context = Context(dict_data)
        html = template.render(context)
    else:
        # May not work anymore since S3 PDF refactoring.
        html = render_to_string(settings.TEMPLATES_PDF_FILEPATHS[type_doc], dict_data)
    pdf_response = HttpResponse(content_type="application/pdf")
    pdf_response["Content-Disposition"] = f'Content-Disposition: attachment; filename="{slugify(filename)}.pdf"'
    weasyprint.HTML(string=html, base_url=base_url).write_pdf(pdf_response)
    return pdf_response


def generate_pdf_binary(context, request, template_name):
    """Generate a PDF file as a binary (used for all PDF notifications attached in emails)."""
    if settings.USE_S3 == True:
        s3 = get_s3_client()
        data = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=template_name)
        template = Template(data['Body'].read().decode('utf-8'))
        context = Context(context)
    else:
        # May not work anymore since S3 PDF refactoring.
        template = get_template(template_name)
    html = template.render(context)
    pdf_binary = weasyprint.HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()
    return pdf_binary
