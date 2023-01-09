from django.http import JsonResponse
from django.template import TemplateSyntaxError
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View

from .models import MailTemplate, MailTemplateVar
from .utils import is_ajax_request


class MailTemplatePreview(View):
    def post(self, request, *args, **kwargs):
        response = {"data": None, "msg": ""}
        pk = kwargs["pk"]

        body = request.POST.get("body", None)
        context_params = {}

        if not body:
            response["msg"] = _("No body for this template provided")
            return JsonResponse(response)

        try:
            template = MailTemplate.objects.get(pk=pk)
        except MailTemplate.DoesNotExist:
            response["msg"] = _("Template #%s can't be found") % pk
            return JsonResponse(response)

        try:
            available_vars = template.available_vars.all()

            # Get multi-valued fakevars
            fakevars_dict = {}
            for template_var in available_vars:
                fake_vars = template_var.fake_vars
                if isinstance(fake_vars, list) and len(fake_vars) > 1:
                    fake_var_lst = []
                    for fv in fake_vars:
                        fake_var_lst.append((type(fv), fv))
                    fakevars_dict[template_var.name] = fake_var_lst
                else:
                    context_params[template_var.name] = (
                        fake_vars[0] if fake_vars else None
                    )
            context_params['fakevars_dict'] = fakevars_dict

            body = template.parse_var_faker_from_string(
                context_params=context_params,
                user=self.request.user,
                request=self.request,
                body=body,
                available_vars=available_vars,
            )
            response["data"] = body
        except TemplateSyntaxError:
            response["msg"] = _("A syntax error occured in template #%s") % pk

        return JsonResponse(response)


class AvailableVarsList(View):
    @method_decorator(is_ajax_request)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(request, *args, **kwargs):
        response = {'msg': '', 'data': []}
        template_id = kwargs['template_id']
        if template_id:
            template_vars = MailTemplateVar.objects.filter(mail_templates=template_id)
            response["data"] = [
                {'id': v.id, 'code': v.code, 'description': v.description}
                for v in template_vars
            ]
        else:
            response["msg"] = _("Error : no template id")

        return JsonResponse(response, safe=False)
