""" Custom permissions for users """
from rest_framework.permissions import BasePermission


class ViewAssociationUserPermission(BasePermission):

    def has_permission(self, request, view):
        user_id = view.kwargs.get("user_id")
        return request.user.id == user_id or request.user.has_perm("users.view_associationuser_anyone")


class AddAssociationUserPermission(BasePermission):

    def has_permission(self, request, view):
        # TODO Remove is_staff check to use another helper.
        if request.user.is_staff or request.user.is_staff_for_association(request.data.get("association")):
            return True
        if request.user.pk == int(request.data.get("user")):
            return True
        return False
