import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ..models import MailTemplate, MailTemplateVar

User = get_user_model()


class ViewsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser('admin')
        cls.headers = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        cls.template_var = MailTemplateVar.objects.create(
            code='{{ username }}', description='Login'
        )
        cls.mail_template = MailTemplate.objects.create(
            code='TPL',
            label='template',
            description='empty template',
            subject='tpl',
            body='This is a template',
        )
        cls.mail_template.available_vars.add(cls.template_var)

    def test_list_available_vars(self):
        self.client.force_login(self.admin_user)
        url = reverse(
            'mail_template:available_vars-list',
            kwargs={'template_id': self.mail_template.id},
        )
        response = self.client.get(url, **self.headers)
        content = json.loads(response.content.decode())

        self.assertEqual(content['msg'], '')
        self.assertEqual(len(content['data']), 1)
        var = content['data'][0]
        self.assertEqual(var['id'], self.template_var.pk)

    def test_empty_available_vars(self):
        self.client.force_login(self.admin_user)
        url = reverse('mail_template:available_vars-list', kwargs={'template_id': 0})
        response = self.client.get(url, **self.headers)
        content = json.loads(response.content.decode())
        self.assertEqual(content["msg"], _("Error : no template id"))
        self.assertEqual(content['data'], [])
