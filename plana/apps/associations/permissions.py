from rest_framework import permissions

from django.utils.translation import gettext_lazy as _


class AssociationRetrieveUpdateDestroyPermission(permissions.BasePermission):

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
