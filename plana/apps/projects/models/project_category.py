"""Models describing categories linked to projects."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class ProjectCategory(models.Model):
    """Main model."""

    project = models.ForeignKey(
        "Project",
        verbose_name=_("Project"),
        on_delete=models.CASCADE,
    )
    category = models.ForeignKey(
        "Category",
        verbose_name=_("Project Category"),
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.project} {self.category}"

    class Meta:
        verbose_name = _("Project category")
        verbose_name_plural = _("Projects categories")
        permissions = [
            (
                "view_projectcategory_all",
                "Can view all categories linked to a project.",
            ),
        ]
