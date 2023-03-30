"""Models describing institutions (Crous, Unistra, UHA, ...)."""
from django.apps import apps
from django.db import models
from django.utils.translation import gettext_lazy as _


class Institution(models.Model):
    """Main model."""

    name = models.CharField(_("Name"), max_length=250, blank=False)
    acronym = models.CharField(_("Acronym"), max_length=30, blank=False)

    def __str__(self):
        return f"{self.name} ({self.acronym})"

    def default_institution_managers(self):
        """Return the best list of managers to contact for an institution."""
        default_institution_managers_query = apps.get_model(
            "users.user"
        ).objects.filter(
            is_superuser=False,
            pk__in=apps.get_model("users.groupinstitutioncommissionuser")
            .objects.filter(institution_id=self.pk)
            .values_list("user_id"),
        )
        better_institution_managers_query = default_institution_managers_query.filter(
            pk__in=apps.get_model("users.user")
            .objects.annotate(num_groups=models.Count("groupinstitutioncommissionuser"))
            .filter(num_groups__lt=2)
            .values_list("id", flat=True)
        )
        query_to_return = default_institution_managers_query
        if better_institution_managers_query.count() > 0:
            query_to_return = better_institution_managers_query
        return query_to_return.values_list("first_name", "last_name", "email")

    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institutions")
