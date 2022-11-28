from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .admin_forms import MailTemplateForm
from .models import MailTemplate, MailTemplateVar


@admin.register(MailTemplate)
class MailTemplateAdmin(SummernoteModelAdmin):
    form = MailTemplateForm
    list_display = ('code', 'label', 'active')
    filter_horizontal = ('available_vars',)
    summernote_fields = ('body',)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        
        fakevars_dict = {}
        qs = MailTemplateVar.objects \
            .prefetch_related(*(
                f'{MailTemplateVar.fakevars_relation_name(rel)}_set' 
                for rel in MailTemplateVar.fakevars_relations()
            )) \
            .filter(mail_templates__id=object_id)

        for template_var in qs:
            if (len(fakevars := template_var.fakevars) > 1):
                fakevars_dict[template_var.code] = [(f.pk, f.value) for f in fakevars]
        extra_context['fakevars'] = fakevars_dict

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
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
