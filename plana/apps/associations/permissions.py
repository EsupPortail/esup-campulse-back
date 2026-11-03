"""Base permissions classes for associations"""

from django.utils.translation import gettext_lazy as _
from rest_framework import permissions

from plana.apps.associations.models import Association


class AssociationRetrievePermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            
            if request.user.is_anonymous and (not obj.is_enabled or not obj.is_public):
                self.message = _("Association not visible.")
                return False

            if not request.user.is_anonymous and not request.user.is_in_association(obj.pk):

                if (
                    not obj.is_enabled
                    and not request.user.has_perm("associations.view_association_not_enabled")
                ):
                    self.message = _("Association not enabled.")
                    return False
                if (
                    not obj.is_public
                    and not request.user.has_perm("associations.view_association_not_public")
                ):
                    self.message = _("Association not public.")
                    return False

        return True


class AssociationUpdatePermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if (
                request.user.is_president_in_association(obj.id)
                or request.user.has_perm("associations.change_association_any_institution")
                or request.user.is_staff_in_institution(obj.institution_id)
        ):
            return True
        return False


class AssociationDestroyPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.is_enabled:
            self.message = _("Can't delete an enabled association.")
            return False
        if request.user.has_perm("associations.change_association_any_institution") or request.user.is_staff_in_institution(obj.institution_id):
            return True
        return False


class ViewAssociationMembersPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        asso_id = view.kwargs.get("association_id")
        return Association.objects.managed_by_user(request.user).filter(id=asso_id).exists() or request.user.is_in_association(asso_id)
