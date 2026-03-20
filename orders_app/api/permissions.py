from rest_framework.permissions import BasePermission, IsAuthenticated

from profile_app.models import Profile


class IsCustomerUser(IsAuthenticated):
    """Permission allowing access only to authenticated customer users."""

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False

        try:
            profile = Profile.objects.get(user=request.user)
            return profile.type == 'customer'
        except Profile.DoesNotExist:
            return False


class IsOrderBusinessUser(BasePermission):
    """Only the assigned business user may update an order."""

    def has_object_permission(self, request, view, obj):
        return request.user == obj.business_user
