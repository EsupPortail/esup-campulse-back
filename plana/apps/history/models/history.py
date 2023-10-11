"""Models describing history log for superadmins."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.associations.models.association import Association
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.projects.models.project import Project
from plana.apps.users.models.user import AssociationUser, GroupInstitutionFundUser, User


class History(models.Model):
    """Main model."""

    class ActionType(models.TextChoices):
        """List of logged actions."""

        USER_LOGGED = "USER_LOGGED", _("A user is logged in")
        USER_REGISTERED = "USER_REGISTERED", _("A user is registered")
        USER_VALIDATED = "USER_VALIDATED", _("A user is validated")
        ASSOCIATION_CHANGED = "ASSOCIATION_CHANGED", _("An association is changed")
        ASSOCIATION_CHARTER_CHANGED = "ASSOCIATION_CHARTER_CHANGED", _("An association charter is changed")
        ASSOCIATION_USER_VALIDATED = "ASSOCIATION_USER_VALIDATED", _(
            "A link between an association and a user is validated"
        )
        ASSOCIATION_USER_CHANGED = "ASSOCIATION_USER_CHANGED", _("A link between an association and a user is changed")
        ASSOCIATION_USER_DELEGATION_CHANGED = "ASSOCIATION_USER_DELEGATION_CHANGED", _(
            "A delegation between an association and a user is changed"
        )
        GROUP_INSTITUTION_FUND_USER_CHANGED = "GROUP_INSTITUTION_FUND_USER_CHANGED", _(
            "A link between group and user is changed"
        )
        DOCUMENT_UPLOAD_CHANGED = "DOCUMENT_UPLOAD_CHANGED", _("A document upload is changed")
        PROJECT_VALIDATED = "PROJECT_VALIDATED", _("A project is validated")

    action_title = models.CharField(
        _("Action title"),
        max_length=64,
        choices=ActionType.choices,
    )
    action_user = models.ForeignKey(
        User,
        verbose_name=_("User who did action"),
        related_name="action_user_set",
        on_delete=models.CASCADE,
    )
    creation_date = models.DateTimeField(_("Creation date"), auto_now_add=True)
    user = models.ForeignKey(
        User,
        verbose_name=_("User affected by change"),
        related_name="user_set",
        on_delete=models.CASCADE,
        null=True,
    )
    association = models.ForeignKey(
        Association,
        verbose_name=_("Association affected by change"),
        on_delete=models.CASCADE,
        null=True,
    )
    association_user = models.ForeignKey(
        AssociationUser,
        verbose_name=_("Link between association and user affected by change"),
        on_delete=models.CASCADE,
        null=True,
    )
    group_institution_fund_user = models.ForeignKey(
        GroupInstitutionFundUser,
        verbose_name=_("Link between group and user affected by change"),
        on_delete=models.CASCADE,
        null=True,
    )
    document_upload = models.ForeignKey(
        DocumentUpload,
        verbose_name=_("Document affected by change"),
        on_delete=models.CASCADE,
        null=True,
    )
    project = models.ForeignKey(
        Project,
        verbose_name=_("Project affected by change"),
        on_delete=models.CASCADE,
        null=True,
    )

    def __str__(self):
        return f"{self.action_title}"

    class Meta:
        verbose_name = _("History")
        verbose_name_plural = _("History")
