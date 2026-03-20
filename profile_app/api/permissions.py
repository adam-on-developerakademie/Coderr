from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission


class IsProfileOwnerOrReadOnly(BasePermission):
    """Allow authenticated access and restrict write access to profile owners."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        if obj.user != request.user:
            raise PermissionDenied(
                f"You are not allowed to access profile data for user {obj.user.username}. "
                f"You may only edit your own profile (user ID: {request.user.id})."
            )

        return True
