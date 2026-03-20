from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from profile_app.models import Profile


class IsBusinessUserPermission(permissions.BasePermission):
    """Allow write operations only for authenticated business users."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        try:
            profile = Profile.objects.get(user=request.user)
            return profile.type == 'business'
        except Profile.DoesNotExist:
            return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow write operations only for the offer owner."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        return obj.user == request.user


class OfferCreatePermission:
    """Helper for create-specific business-profile validation responses."""

    @staticmethod
    def denied_response_for_user(user):
        try:
            profile = Profile.objects.get(user=user)
            if profile.type != 'business':
                return Response(
                    {"error": "Only business users can create offers"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except Profile.DoesNotExist:
            return Response(
                {"error": "User profile not found"},
                status=status.HTTP_403_FORBIDDEN,
            )

        return None
