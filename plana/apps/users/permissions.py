""" Custom permissions for users """
from rest_framework.permissions import BasePermission


class ViewAssociationUserPermission(BasePermission):

    def has_permission(self, request, view):
        user_id = view.kwargs.get("user_id")
        return request.user.id == user_id or request.user.has_perm("users.view_associationuser")
