from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from profile_app.models import Profile


class IsReviewerOrReadOnly(permissions.BasePermission):
    """Only the reviewer may perform PATCH/DELETE operations."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return obj.reviewer == request.user


class ReviewCreatePermission:
    """Helper for create-specific customer-profile validation responses."""

    @staticmethod
    def denied_response_for_user(user):
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response(
                {"detail": "Only authenticated users with a customer profile can create reviews."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if profile.type != 'customer':
            return Response(
                {"detail": "Only authenticated users with a customer profile can create reviews."},
                status=status.HTTP_403_FORBIDDEN,
            )

        return None
