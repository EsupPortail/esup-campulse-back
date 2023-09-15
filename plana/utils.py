"""Generic functions to send emails, and convert "true" and "false" to real booleans."""
import ast
import datetime

import weasyprint
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
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
            mail.attach(
                temp_attachment["filename"],
                create_pdf(
                    temp_attachment["context_attach"],
                    temp_attachment["request"],
                    temp_attachment["template_name"],
                ),
                temp_attachment["mimetype"],
            )

    mail.send()


def to_bool(attr):
    """Translate strings like "true"/"false" into boolean."""

    if isinstance(attr, bool):
        return attr
    if isinstance(attr, str):
        return ast.literal_eval(attr.capitalize())
    return None


def valid_date_format(date):
    """Checks date format without time."""

    date_format = "%Y-%m-%d"
    try:
        datetime.datetime.strptime(date, date_format)
    except ValueError:
        return False
    return True


def generate_pdf(filename, dict_data, type_doc, base_url):
    """Generate a PDF file depending on the process."""

    html = render_to_string(settings.TEMPLATES_PDF[type_doc], dict_data)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'Content-Disposition: attachment; filename="{slugify(filename)}.pdf"'
    weasyprint.HTML(string=html, base_url=base_url).write_pdf(response)
    return response


def create_pdf(context, request, template_name):
    template = get_template(template_name)
    html = template.render(context)
    pdf_binary = weasyprint.HTML(string=html, base_url=request.build_absolute_uri('/')).write_pdf()
    return pdf_binary
