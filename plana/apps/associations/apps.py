from django.apps import AppConfig
from health_check.plugins import plugin_dir


class AssociationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "plana.apps.associations"

    def ready(self):
        from plana.apps.associations.backends import AssociationCheckBackend

        plugin_dir.register(AssociationCheckBackend)
