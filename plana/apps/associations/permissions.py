"""Base permissions classes for associations"""

from rest_framework import permissions

from plana.apps.associations.models import Association


class AssociationManagePermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if (
            request.user.has_perm("associations.change_association_any_institution")
            or request.user.is_staff_in_institution(obj.institution_id)
        ):
            return True

        if request.method == "GET" and request.user.is_in_association(obj.id):
            return True

        elif request.method == "PATCH" and request.user.is_president_in_association(obj.id):
            return True

        return False


class ViewAssociationMembersPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        asso_id = view.kwargs.get("association_id")
        return Association.objects.managed_by_user(request.user).filter(id=asso_id).exists() or request.user.is_in_association(asso_id)
