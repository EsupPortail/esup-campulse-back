from django.http import JsonResponse
from django.template import TemplateSyntaxError
from django.views import View

from .models import MailTemplate, MailTemplateVar
from .utils import is_ajax_request


class MailTemplatePreviewAPI(View):
    def post(self, request, *args, **kwargs):
        response = {"data": None, "msg": ""}
        pk = kwargs["pk"]

        body = request.POST.get("body", None)
        context_params = {
            "user_is": request.POST.get("user_group", "estetudiant"),
            "slot_type": request.POST.get("slot_type", "estuncours"),
            "local_account": request.POST.get("local_user", "true").strip().lower() == "true",
            "remote": request.POST.get("remote", "true").strip().lower() == "true",
        }

        if not body:
            response["msg"] = _("No body for this template provided")
            return JsonResponse(response)

        try:
            template = MailTemplate.objects.get(pk=pk)
        except MailTemplate.DoesNotExist:
            response["msg"] = _("Template #%s can't be found") % pk
            return JsonResponse(response)

        try:
            body = template.parse_var_faker_from_string(
                context_params=context_params,
                user=self.request.user,
                request=self.request,
                body=body
            )
            response["data"] = body
        except TemplateSyntaxError:
            response["msg"] = _("A syntax error occured in template #%s") % pk

        return JsonResponse(response)


@is_ajax_request
def ajax_get_available_vars(request, template_id=None):
    response = {'msg': '', 'data': []}

    if template_id:
        template_vars = MailTemplateVar.objects.filter(mail_templates=template_id)
        response["data"] = [{'id': v.id, 'code': v.code, 'description': v.description} for v in template_vars]
    else:
        response["msg"] = gettext("Error : no template id")

    return JsonResponse(response, safe=False)
