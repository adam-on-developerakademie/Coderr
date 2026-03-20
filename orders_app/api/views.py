from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from django.contrib.auth.models import User
from orders_app.models import Order
from orders_app.api.filters import (
    business_profile_exists,
    get_completed_order_count_for_business_user,
    get_in_progress_order_count_for_business_user,
    get_orders_for_user,
)
from orders_app.api.permissions import IsCustomerUser, IsOrderBusinessUser
from orders_app.api.serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer
)


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
            return [IsAuthenticated(), IsOrderBusinessUser()]
        elif self.action == 'destroy':
            return [IsAdminUser()]
        else:
            return [IsAuthenticated()]
    
    def get_queryset(self):
        """Limit list endpoint to orders linked to the current user.
        # Do not restrict detail endpoints for retrieve/update/destroy.
        # Return full queryset for non-list actions.
        """
        if self.action == 'list':
            return get_orders_for_user(self.request.user)
        return Order.objects.all()
    
    def get_serializer_class(self):
        """Return serializer class based on action."""
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action in ['partial_update', 'update']:
            return OrderStatusUpdateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new order from offer_detail_id.
        # Return full order payload.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        output_serializer = OrderSerializer(order)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, *args, **kwargs):
        """Update order status only.
        # Validate payload before object lookup.
        # This allows 400 responses before 404 responses.
        # Load target instance (may raise 404) and apply object-level permissions.
        # Apply validated status update.
        # Return full order payload.
        """
        serializer = self.get_serializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        output_serializer = OrderSerializer(order)
        return Response(output_serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """Update order status via PUT."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = self.get_object()

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

        if not business_profile_exists(business_user):
            return Response(
                {"detail": "Business user not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        count = get_in_progress_order_count_for_business_user(business_user)
        
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

        if not business_profile_exists(business_user):
            return Response(
                {"detail": "Business user not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        count = get_completed_order_count_for_business_user(business_user)
        
        return Response({"completed_order_count": count}, status=status.HTTP_200_OK)
