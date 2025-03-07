import json

from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .admin_forms import MailTemplateForm
from .models import MailTemplate, MailTemplateVar


class AdminWithRequest:
    """
    Class used to pass request object to admin form
    """

    def get_form(self, request, obj=None, **kwargs):
        AdminForm = super().get_form(request, obj, **kwargs)

        class AdminFormWithRequest(AdminForm):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return AdminForm(*args, **kwargs)

        return AdminFormWithRequest


@admin.register(MailTemplate)
class MailTemplateAdmin(AdminWithRequest, SummernoteModelAdmin):
    form = MailTemplateForm
    list_display = ('code', 'subject', 'active')
    filter_horizontal = ('available_vars',)
    summernote_fields = ('body',)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}

        fakevars_dict = {}
        qs = MailTemplateVar.objects.filter(mail_templates__id=object_id)

        # Get all multi-valued fakevars
        for template_var in qs:
            fake_vars = template_var.fake_vars
            if isinstance(fake_vars, list) and len(fake_vars) > 1:
                # var_type = type(fake_vars[0])
                fake_var_lst = []
                for fv in fake_vars:
                    fake_var_lst.append((type(fv), fv))
                fakevars_dict[template_var.name] = fake_var_lst

        extra_context['fakevars'] = fakevars_dict

        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    class Media:
        css = {
            'all': (
                'mail_template/vendor/jquery-ui/jquery-ui.min.css',
                'mail_template/vendor/datatables/datatables.min.css',
                'mail_template/vendor/datatables/DataTables-1.10.20/css/dataTables.jqueryui.min.css',
            )
        }
        js = (
            'mail_template/vendor/jquery/jquery-3.4.1.min.js',
            'mail_template/vendor/jquery-ui/jquery-ui.min.js',
            'mail_template/mail_templates.js',
            'mail_template/vendor/datatables/datatables.min.js',
            'mail_template/vendor/datatables/datatables.min.js',
        )
