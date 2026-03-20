from rest_framework.permissions import BasePermission


class PublicBaseInfoPermission(BasePermission):
    """Allow public access to base information endpoint."""

    def has_permission(self, request, view):
        return True
