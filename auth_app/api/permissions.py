from rest_framework.permissions import BasePermission


class AllowAnyAuthPermission(BasePermission):
    """Allow public access to authentication endpoints."""

    def has_permission(self, request, view):
        return True
