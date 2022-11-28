import re

from django_summernote.widgets import SummernoteWidget

from django import forms, template
from django.utils.translation import gettext_lazy as _

from .models import MailTemplate, MailTemplateVar


class MailTemplateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.request
        for field in ('label', 'description', 'subject'):
            if self.fields.get(field):
                self.fields[field].widget.attrs['class'] = 'form-control'
                self.fields[field].widget.attrs['size'] = 80

        # if self.fields:
        #     if self.instance.id:
        #         self.fields['code'].disabled = True

        #     if not request.user.is_superuser:
        #         self.fields['available_vars'].widget = forms.MultipleHiddenInput()
        #         self.fields['available_vars'].queryset = self.fields['available_vars'].queryset.order_by('code')
        #     self.fields['available_vars'].required = False

    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get("code", '')
        body = cleaned_data.get("body", '')
        available_vars = cleaned_data.get("available_vars", '')
        valid_user = False

        try:
            user = self.request.user
            valid_user = user.is_superuser
        except AttributeError:
            pass

        if not valid_user:
            raise forms.ValidationError(_("You don't have the required privileges"))

        cleaned_data["code"] = code.upper()

        body_errors_list = []

        # Check variables and raise an error if forbidden ones are found
        forbidden_vars = MailTemplateVar.objects.exclude(code__in=[v.code for v in available_vars])

        forbidden_vars_list = [f_var.code for f_var in forbidden_vars if f_var.code.lower() in body.lower()]

        if forbidden_vars_list:
            forbidden_vars_msg = _("The message body contains forbidden variables : ") + ', '.join(forbidden_vars_list)

            body_errors_list.append(self.error_class([forbidden_vars_msg]))

        # Check for unknown variables in body
        # all_vars = re.findall(r"(\$\{[\w+\.]*\})", body)  # match for ${my_var}
        all_vars = re.findall(r"(\{\{ *[\w+\.]* *\}\})", body)  # match for {{ my_var }}
        unknown_vars = [v for v in all_vars if not MailTemplateVar.objects.filter(code__iexact=v.lower()).exists()]

        # Check for body syntax errors
        try:
            template.Template(body).render(template.Context())
        except template.TemplateSyntaxError as e:

            if "template_debug" in dir(e):
                before: str = e.template_debug["before"]
                line: int = 1 + before.count("<br>") + before.count("</br>")
                line += before.count("&lt;br&gt;") + before.count("&lt;/br&gt;")
                body_syntax_error_msg = _("The message body contains syntax error(s) : ")
                body_syntax_error_msg += _('at "%s" line %s') % (e.template_debug["during"], line)
                body_errors_list.append(self.error_class([body_syntax_error_msg]))
            else:
                body_syntax_error_msg = _("The message body contains syntax error(s) : ") + str(e)
                body_errors_list.append(self.error_class([body_syntax_error_msg]))

        if unknown_vars:
            unknown_vars_msg = _("The message body contains unknown variable(s) : ") + ', '.join(unknown_vars)
            body_errors_list.append(self.error_class([unknown_vars_msg]))

        if body_errors_list:
            raise forms.ValidationError(body_errors_list)

        return cleaned_data

    class Meta:
        model = MailTemplate
        fields = '__all__'
        widgets = {
            'body': SummernoteWidget(),
        }
