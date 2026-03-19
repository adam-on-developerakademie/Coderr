from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.db.models import Q
from orders_app.models import Order
from orders_app.api.serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer
)
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


class IsBusinessUser(IsAuthenticated):
    """Permission allowing access only to authenticated business users."""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        try:
            profile = Profile.objects.get(user=request.user)
            return profile.type == 'business'
        except Profile.DoesNotExist:
            return False


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for order list/create/status-update/delete operations."""
    
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = None
    
    def get_permissions(self):
        """Return action-specific permission instances."""
        if self.action == 'create':
            return [IsCustomerUser()]
        elif self.action in ['partial_update', 'update']:
            return [IsAuthenticated()]
        elif self.action == 'destroy':
            return [IsAdminUser()]
        else:
            return [IsAuthenticated()]
    
    def get_queryset(self):
        """Limit list endpoint to orders linked to the current user."""
        # Do not restrict detail endpoints for retrieve/update/destroy.
        if self.action == 'list':
            user = self.request.user
            return Order.objects.filter(
                Q(customer_user=user) | Q(business_user=user)
            )
        # Return full queryset for non-list actions.
        return Order.objects.all()
    
    def get_serializer_class(self):
        """Return serializer class based on action."""
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['partial_update', 'update']:
            return OrderStatusUpdateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new order from offer_detail_id."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        # Return full order payload.
        output_serializer = OrderSerializer(order)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, *args, **kwargs):
        """Update order status only."""
        # Validate payload before object lookup.
        # This allows 400 responses before 404 responses.
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Load target instance (may raise 404).
        instance = self.get_object()

        # Only the business user assigned to the order can update status.
        if request.user != instance.business_user:
            raise PermissionDenied("You do not have permission to perform this action.")
        
        # Apply validated status update.
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        # Return full order payload.
        output_serializer = OrderSerializer(order)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """Update order status via PUT."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = self.get_object()

        # Only the business user assigned to the order can update status.
        if request.user != instance.business_user:
            raise PermissionDenied("You do not have permission to perform this action.")

        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        output_serializer = OrderSerializer(order)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        """Delete order (staff users only)."""
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderCountView(APIView):
    """Return count of in-progress orders for a business user."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, business_user_id):
        """Count in-progress orders for the given business user id."""
        try:
            business_user = User.objects.get(id=business_user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Business user not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        from profile_app.models import Profile
        if not Profile.objects.filter(user=business_user, type='business').exists():
            return Response(
                {"detail": "Business user not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        count = Order.objects.filter(
            business_user=business_user,
            status='in_progress'
        ).count()
        
        return Response({"order_count": count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    """Return count of completed orders for a business user."""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, business_user_id):
        """Count completed orders for the given business user id."""
        try:
            business_user = User.objects.get(id=business_user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "Business user not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        from profile_app.models import Profile
        if not Profile.objects.filter(user=business_user, type='business').exists():
            return Response(
                {"detail": "Business user not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        count = Order.objects.filter(
            business_user=business_user,
            status='completed'
        ).count()
        
        return Response({"completed_order_count": count}, status=status.HTTP_200_OK)
