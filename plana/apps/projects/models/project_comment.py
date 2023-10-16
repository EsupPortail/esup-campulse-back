"""Models describing comments left on a project by managers."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.users.models.user import User


class ProjectComment(models.Model):
    """Main model."""

    text = models.TextField(_("Text"))
    is_visible = models.BooleanField(_("Is visible"), default=True)
    creation_date = models.DateTimeField(_("Creation date"), auto_now_add=True)
    edition_date = models.DateTimeField(_("Edition date"), auto_now=True)
    project = models.ForeignKey(
        "Project",
        verbose_name=_("Project"),
        related_name="projects",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        related_name="users",
        on_delete=models.CASCADE,
        null=True,
    )

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = _("Project comment")
        verbose_name_plural = _("Projects comments")
        permissions = [
            (
                "view_projectcomment_any_fund",
                "Can view all comments linked to all projects for a fund.",
            ),
            (
                "view_projectcomment_any_institution",
                "Can view all comments linked to all projects for an institution.",
            ),
            (
                "view_projectcomment_not_visible",
                "Can view all comments even if they are restricted.",
            ),
        ]
