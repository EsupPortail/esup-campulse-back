"""Storage field from octant. https://git.unistra.fr/di/cesar/octant/back/-/blob/develop/octant/apps/api/serializers/fields.py ."""
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from thumbnails.files import ThumbnailedImageFile


@extend_schema_field(OpenApiTypes.OBJECT)
class ThumbnailField(serializers.ReadOnlyField):
    """Read-only field for all sizes of a Thumbnail image."""

    def __init__(self, **kwargs):
        help_text = kwargs.pop("help_text", _("URL for each thumbnail size"))
        if sizes := kwargs.pop("sizes", None):
            self.sizes = sizes
        else:
            self.sizes = [
                size for size in settings.THUMBNAILS["SIZES"] if size != "base"
            ]

        super().__init__(help_text=help_text, **kwargs)

    def to_representation(self, value: ThumbnailedImageFile):
        if not value:
            return {}
        return {size: value.thumbnails.get(size).url for size in self.sizes}
