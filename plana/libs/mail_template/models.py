import re

from django.db import models
from django.utils.translation import gettext_lazy as _

from . import managers


class MailTemplateVar(models.Model):
    code = models.CharField(_("Code"), max_length=64, blank=False, null=False, unique=True)
    description = models.CharField(_("Description"), max_length=128, blank=False, null=False, unique=True)

    objects = managers.MailTemplateVarQuerySet.as_manager()

    @property
    def name(self):
        try:
            return re.match(r'\{\{ *([\w.\-_]*) *\}\}', self.code).groups()[0]
        except AttributeError:
            return ''

    @classmethod
    def fakevars_relations(cls):
        return [rel for r in cls._meta.related_objects
                if issubclass((rel := r.related_model), FakeVar)]

    @classmethod
    def fakevars_relation_name(cls, rel):
        return rel.__name__.lower()

    @classmethod
    def fakevars_relations_names(cls):
        return list(map(cls.fakevars_relation_name, cls.fakevars_relations()))

    @property
    def fakevars(self):
        results = []
        for rel in self.fakevars_relations_names():
            results.extend(list(getattr(self, f'{rel}_set').all()))
        return results

    def __str__(self):
        return f"{self.code} : {self.description}"

    class Meta:
        verbose_name = _('Template variable')
        verbose_name_plural = _('Template variables')
        ordering = ['code', ]


class MailTemplate(models.Model):
    """
    Mail templates with HTML content
    """

    code = models.CharField(_("Code"), max_length=128, blank=False, null=False, unique=True)
    label = models.CharField(_("Label"), max_length=128, blank=False, null=False, unique=True)
    description = models.CharField(_("Description"), max_length=512, blank=False, null=False)
    subject = models.CharField(_("Subject"), max_length=256, blank=False, null=False)
    body = models.TextField(_("Body"), blank=False, null=False)
    active = models.BooleanField(_("Active"), default=True)

    available_vars = models.ManyToManyField(
        MailTemplateVar, related_name='mail_templates', verbose_name=_("Available variables"),
    )

    def __str__(self):
        return f"{self.code} : {self.label}"


    # def parse_vars(self, user, request, **kwargs):
    #     from .utils import parser

    #     return parser(
    #         user=user,
    #         request=request,
    #         message_body=self.body,
    #         vars=self.available_vars.all(), **kwargs,
    #     )

    # def parse_vars_faker(self, user, request, **kwargs):
    #     from .utils import parser_faker
    #     return parser_faker(
    #         user=user,
    #         request=request,
    #         message_body=self.body,
    #         available_vars=self.available_vars.all(),
    #         **kwargs,
    #     )

    def parse_var_faker_from_string(
        self, user, body, request, context_params, available_vars=None, **kwargs):
        from .utils import parser_faker
        return parser_faker(
            context_params=context_params,
            user=user,
            request=request,
            message_body=body,
            available_vars=available_vars or self.available_vars.all(),
            **kwargs,
        )

    @property
    def monovalued_fakevars(self):
        rel_names = MailTemplateVar.fakevars_relations_names()
        return [fv for fv in self.available_vars.prefetch_fakevars().fakevar_counts()
                if sum(getattr(fv, f'{rel}_cnt') for rel in rel_names) == 1]

    @property
    def multivalued_fakevars(self):
        rel_names = MailTemplateVar.fakevars_relations_names()
        return [fv for fv in self.available_vars.prefetch_fakevars().fakevar_counts()
                if sum(getattr(fv, f'{rel}_cnt') for rel in rel_names) > 1]

    class Meta:
        verbose_name = _('Mail template')
        verbose_name_plural = _('Mail templates')
        ordering = ['label', ]


class FakeVar(models.Model):
    template_var = models.ForeignKey(MailTemplateVar, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    @property
    def var_type(self):
        return re.match(r'FakeVar(\w*)', self.__class__.__name__).groups()[0].lower()

class FakeVarText(FakeVar):
    value = models.TextField(_("Value"))


class FakeVarInt(FakeVar):
    value = models.IntegerField(_("Value"))


class FakeVarBool(FakeVar):
    value = models.BooleanField(_("Value"))
