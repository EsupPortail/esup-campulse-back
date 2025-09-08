"""Admin view for User models."""

import secrets
import string

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import password_validation
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.models import Group, User
from django.utils.translation import gettext_lazy as _

from plana.apps.institutions.models.institution import Institution
from plana.apps.users.provider import CASProvider

from ...admin import SecuredInlineAdmin, SecuredModelAdmin
from .models import AssociationUser, GroupInstitutionFundUser, User


class ManagerUserCreationForm(UserCreationForm):
    """Custom UserCreationForm."""

    email = forms.EmailField(label=_("Email"))
    first_name = forms.CharField(label=_("First name"))
    last_name = forms.CharField(label=_("Last name"))
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validation.password_validators_help_text_html(),
        required=False,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=_("Enter the same password as before, for verification."),
        required=False,
    )
    username = forms.CharField(
        label=_("Username"), required=False, help_text=_("Change only if CAS account, with its identifier.")
    )
    is_superuser = forms.BooleanField(label=_("Is superuser"), required=False)
    is_manager_general = forms.BooleanField(label=_("Is Manager General"), required=False)

    def save(self, commit=True):
        """Set groups in an easier way."""
        user = super().save(commit=False)
        user.is_active = True
        user.is_staff = True
        user.is_validated_by_admin = True
        commit = True

        if "password1" not in self.cleaned_data:
            user.set_password(
                "".join(
                    secrets.choice(string.ascii_letters + string.digits)
                    for i in range(settings.DEFAULT_PASSWORD_LENGTH)
                )
            )
        else:
            user.set_password(self.cleaned_data["password1"])

        is_cas = True
        if "username" not in self.changed_data and user.username == "":
            is_cas = False
            user.username = self.cleaned_data["email"]

        if commit:
            user.save()
            if hasattr(self, "save_m2m"):
                self.save_m2m()

        EmailAddress.objects.create(email=user.email, verified=True, primary=True, user_id=user.id)
        if is_cas:
            SocialAccount.objects.create(
                user=user,
                provider=CASProvider.id,
                uid=user.username,
                extra_data={},
            )

        group = Group.objects.get(name="MANAGER_GENERAL")
        if "is_manager_general" in self.changed_data and self.cleaned_data["is_manager_general"]:
            for institution_id in Institution.objects.values_list("id", flat=True):
                GroupInstitutionFundUser.objects.create(
                    user_id=user.id,
                    group_id=group.id,
                    institution_id=institution_id,
                )

        return user

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "username", "is_superuser"]


# FIXME : May be removed after cleanup
class GroupInstitutionFundUserForm(forms.ModelForm):
    """Custom form for GroupInstitutionFundUser StackedInline to make fields optional."""
    class Meta:
        model = GroupInstitutionFundUser
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["institution"].required = False


class GroupInstitutionFundUserInline(SecuredInlineAdmin):
    """Add GroupInstitutionFundUser sub-form."""

    model = GroupInstitutionFundUser
    fields = ["group", "institution"]
    form = GroupInstitutionFundUserForm


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'
        exclude = ('password',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """List view for users, and define new way to manage user."""

    add_form = ManagerUserCreationForm
    change_form = CustomUserChangeForm
    inlines = [GroupInstitutionFundUserInline]

    list_display = [
        "email",
        "first_name",
        "last_name",
        "get_groups",
        "get_associations",
        "is_validated_by_email",
        "is_cas",
        "is_validated_by_admin",
        "can_submit_projects",
    ]
    list_filter = ["is_validated_by_admin", "can_submit_projects"]
    search_fields = ["email", "first_name", "last_name"]

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .prefetch_related(
                'groupinstitutionfunduser_set__group',
                'associations',
                'emailaddress_set'
            )
        )

    def get_form(self, request, obj=None, **kwargs):
        """Route correct form if user is created or changed."""
        if not obj:
            self.form = self.add_form
        else:
            self.form = self.change_form

        return super().get_form(request, obj, **kwargs)

    @admin.display(description=_("Groups"))
    @admin.display(ordering="groups_institutions_funds")
    def get_groups(self, obj):
        """Get groups linked to user."""
        return list({gifu.group.name for gifu in obj.groupinstitutionfunduser_set.all()})

    @admin.display(description=_("Associations"))
    @admin.display(ordering="associationuser")
    def get_associations(self, obj):
        """Get associations linked to user."""
        return [asso.acronym for asso in obj.associations.all()]

    @admin.display(boolean=True)
    @admin.display(description=_("Has validated email address"))
    @admin.display(ordering="emailaddress")
    def is_validated_by_email(self, obj):
        return obj.has_validated_email_user

    @admin.display(boolean=True)
    @admin.display(description=_("Is CAS user"))
    @admin.display(ordering="socialaccount")
    def is_cas(self, obj):
        return obj.is_cas_user


@admin.register(AssociationUser)
class AssociationUserAdmin(admin.ModelAdmin):
    """List view for association users."""

    list_display = [
        "user",
        "association",
        "is_validated_by_admin",
        "is_president",
        "can_be_president_from",
        "can_be_president_to",
    ]
    list_filter = ["is_validated_by_admin", "is_president"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "association__acronym",
        "association__name",
        "can_be_president_from",
        "can_be_president_to",
    ]


@admin.register(GroupInstitutionFundUser)
class GroupInstitutionFundUserAdmin(SecuredModelAdmin):
    """List view for group users."""

    list_display = ["user", "group", "institution", "fund"]
    search_fields = [
        "user__first_name",
        "user__last_name",
        "group__name",
        "institution__acronym",
        "institution__name",
        "fund__acronym",
        "fund__name",
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'group', 'institution', 'fund')
