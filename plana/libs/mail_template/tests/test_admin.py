from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict
from django.test import TestCase

from ..admin_forms import MailTemplateForm
from ..models import MailTemplate, MailTemplateVar


User = get_user_model()


class AdminFormsTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_superuser('admin')
        cls.template_var = MailTemplateVar.objects.create(
            code='{{ username }}', description='Login')
        cls.mail_template = MailTemplate.objects.create(
            code='TPL', label='template', description='empty template',
            subject='tpl', body='This is a template'
        )
        cls.mail_template.available_vars.add(cls.template_var)
 
    def test_mail_template_creation_success(self):
        self.client.force_login(self.admin_user)
        request = self.client.request().wsgi_request
        data = {
            'label': 'my text',
            'code': 'my code',
            'subject': 'the mail subject',
            'body':'test content',
            'description': 'test desc',
            'active': True,
            'available_vars': [self.template_var]
        }
        form = MailTemplateForm(data=data, request=request)

        self.assertTrue(form.is_valid())
        mail_template = form.save()
        self.assertTrue(MailTemplate.objects.filter(label=data['label']).exists())
        self.assertEqual(mail_template.body, 'test content')

    def test_mail_template_update(self):
        self.client.force_login(self.admin_user)
        request = self.client.request().wsgi_request
        data = model_to_dict(self.mail_template)
        data["body"] = "New mail body"
        form = MailTemplateForm(instance=self.mail_template, request=request, data=data)

        self.assertTrue(form.is_valid())
        mail_template = form.save()
        self.assertEqual(mail_template.body, 'New mail body')

    def test_mail_tempalte_update_error(self):
        self.client.force_login(self.admin_user)
        request = self.client.request().wsgi_request
        data = model_to_dict(self.mail_template)
        data["body"] = "Bad syntax in body {% elif %}"
        form = MailTemplateForm(instance=self.mail_template, request=request, data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Invalid block tag on line 1: 'elif'.", form.errors["__all__"][0])
