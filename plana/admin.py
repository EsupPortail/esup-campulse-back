# Base mixins and custom classes for objects admins
import json
from django import forms
from django.contrib import admin, messages
from django.db import transaction, IntegrityError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class SecuredModelAdmin(admin.ModelAdmin):

    def has_module_permission(self, request):
        return super().has_module_permission(request) and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return super().has_view_permission(request, obj=obj) and request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj=obj) and request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj=obj) and request.user.is_superuser

    def has_add_permission(self, request):
        return super().has_add_permission(request) and request.user.is_superuser


class SecuredInlineAdmin(admin.StackedInline):

    def has_module_permission(self, request):
        return super().has_module_permission(request) and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return super().has_view_permission(request, obj=obj) and request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj=obj) and request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj=obj) and request.user.is_superuser

    def has_add_permission(self, request, obj):
        return super().has_add_permission(request, obj) and request.user.is_superuser


class JSONImportFormMixin(forms.ModelForm):
    """
    Custom Admin Form to toggle between classic object form and JSON file field mass data import (either one or the other)
    JSON mass data import should only be used by a superuser
    """
    use_json_import = forms.BooleanField(
        required=False,
        label=_("Toggle JSON Import Mode"),
        help_text=_("Check this box to import data through a JSON file instead of the classic form. (multiple objects creation)")
    )
    json_file = forms.FileField(
        required=False,
        label=_("JSON file to import data from"),
        widget=forms.ClearableFileInput(attrs={"accept": ".json,application/json"})
    )

    def __init__(self, *args, **kwargs):
        """
        Ignore other fields in the form if JSON data import is toggled
        It's either JSON data import or single objects creation through base form at a time, not both
        """
        super().__init__(*args, **kwargs)
        if self.data.get("use_json_import"):
            for name, field in self.fields.items():
                if name not in ("use_json_import", "json_file"):
                    field.required = False

    def clean(self):
        """
        Ignore other fields in the form if JSON data import is toggled
        It's either JSON data import or single objects creation through base form at a time, not both
        """
        cleaned_data = super().clean()
        if cleaned_data.get("use_json_import"):
            uploaded_file = cleaned_data.get("json_file")
            if not uploaded_file:
                self.add_error("json_file", _("JSON file upload is mandatory in this mode, provide one, or else uncheck the toggle mode box."))
                return cleaned_data
            try:
                content = uploaded_file.read().decode("utf-8")
                parsed = json.loads(content)
                if not isinstance(parsed, list):
                    self.add_error("json_file", _("The provided json file must contain a list of objects : [{...}, {...}]."))
                    return cleaned_data
                cleaned_data["json_objects"] = parsed
            except UnicodeDecodeError:
                self.add_error("json_file", _("The provided JSON file must be encoded in UTF-8."))
            except json.JSONDecodeError as e:
                self.add_error("json_file", f"JSON error : {e}")
        return cleaned_data

    def _post_clean(self):
        """
        Ignore data validation of other fields in the form if JSON data import is toggled
        It's either JSON data import or single objects creation through base form at a time, not both
        """
        if self.cleaned_data.get("use_json_import"):
            return
        super()._post_clean()


class JSONImportAdminMixin(admin.ModelAdmin):
    """
    Custom ModelAdmin Mixin to toggle between classic object creation and JSON file mass data import
    JSON mass data import should only be used by a superuser
    """
    form = JSONImportFormMixin
    json_import_fieldset_title = _("Details")

    class Media:
        js = ("js/admin/toggle_json_import.js",)

    def get_fieldsets(self, request, obj=None):
        """The toggle for JSON data import mode should always appear on top of the form"""
        if request.user.is_superuser and obj is None:
            model_fields = [
                f.name for f in self.model._meta.fields
                if f.editable and f.name != "id"
            ]
            return (
                (None, {"fields": ("use_json_import", "json_file")}),
                (self.json_import_fieldset_title, {"fields": tuple(model_fields)}),
            )
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """JSON data import option is only available for superuser"""
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser or obj is not None:
            form.base_fields.pop("use_json_import", None)
            form.base_fields.pop("json_file", None)
        return form

    def save_model(self, request, obj, form, change):
        """
        Custom save, if a JSON data import is provided, bulk create objects (if error, none is created)
        if not, classic unique object save through base form
        """
        if request.user.is_superuser and form.cleaned_data.get("use_json_import"):
            json_objects = form.cleaned_data.get("json_objects")
            try:
                with transaction.atomic():
                    objects_to_create = [self.model(**item) for item in json_objects]
                    self.model.objects.bulk_create(objects_to_create)
                self.message_user(
                    request,
                    f"{len(objects_to_create)} objects created through the provided JSON file."
                )
            except (IntegrityError, TypeError) as e:
                self.message_user(
                    request,
                    f"Import failed, operation aborted : {e}",
                    level=messages.ERROR
                )
        else:
            super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        """Avoid empty green flag when importing JSON data (either success or error)"""
        if request.POST.get("use_json_import"):
            opts = self.model._meta
            changelist_url = reverse(f"admin:{opts.app_label}_{opts.model_name}_changelist")
            return HttpResponseRedirect(changelist_url)
        return super().response_add(request, obj, post_url_continue)
