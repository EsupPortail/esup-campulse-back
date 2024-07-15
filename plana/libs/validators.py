"""Validators file from Immersion https://git.unistra.fr/di/immersionlyceens/-/blob/develop/immersionlyceens/libs/validators.py ."""

import json
import os

import jsonschema
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from referencing import Registry


@deconstructible
class JsonSchemaValidator:
    """Validate JSON fields in database."""

    # Scandal : some parts here are from ThierrYxxxxxx

    messages = {'invalid': _('Error : %(exception)s')}

    def __init__(self, schema_path):
        """Load JSON schema."""
        self.schema_path = schema_path
        with open(self.schema_path, encoding="utf8") as f:
            self.schema = json.load(f)
        schema_dir = os.path.dirname(self.schema_path)
        schema_uri = f'file://{schema_dir}/'

        # RefResolver is used to resolve the local references
        # https://github.com/Julian/jsonschema/issues/343#issuecomment-319482350
        # https://stackoverflow.com/a/33124971
        # self.schema_resolver = jsonschema.RefResolver(schema_uri, self.schema)
        self.schema_resolver = Registry().with_resource(schema_uri, self.schema)

    def __call__(self, value):
        """Validate field with schema."""
        if value:
            try:
                jsonschema.validate(instance=value, schema=self.schema, resolver=self.schema_resolver)
            except jsonschema.exceptions.ValidationError as msg:
                raise ValidationError(self.messages['invalid'], params={'exception': msg}) from msg

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.schema_name == other.schema_name
