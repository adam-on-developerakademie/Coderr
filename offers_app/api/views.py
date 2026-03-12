from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response

from profile_app.models import Profile

from offers_app.models import Offer, OfferDetail
from offers_app.api.filters import OfferFilter
from offers_app.api.serializers import (
    OfferListSerializer, OfferDetailViewSerializer, OfferCreateUpdateSerializer,
    OfferDetailSerializer, OfferResponseWithFullDetailsSerializer
)


class IsBusinessUserPermission(permissions.BasePermission):
    """Allow write operations only for authenticated business users."""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Read-only operations require authentication only.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write operations require business profile type.
        try:
            profile = Profile.objects.get(user=request.user)
            return profile.type == 'business'
        except Profile.DoesNotExist:
            return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow write operations only for the offer owner."""
    def has_object_permission(self, request, view, obj):
        # Read access for authenticated users.
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write access for owner only.
        return obj.user == request.user


class OfferViewSet(viewsets.ModelViewSet):
    """ViewSet for offer CRUD operations."""
    queryset = Offer.objects.all()
    permission_classes = [IsBusinessUserPermission, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'created_at']
    ordering = ['-updated_at']
    
    def get_serializer_class(self):
        """
        Return different serializers for different actions
        """
        if self.action == 'list':
            return OfferListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return OfferCreateUpdateSerializer
        else:  # retrieve
            return OfferDetailViewSerializer
    
    def get_queryset(self):
        """Build queryset with optional min_price ordering annotation."""
        queryset = Offer.objects.select_related('user').prefetch_related('details')

        # Custom ordering by computed min price.
        ordering = self.request.query_params.get('ordering')
        if ordering == 'min_price':
            from django.db.models import Min
            queryset = queryset.annotate(min_detail_price=Min('details__price')).order_by('min_detail_price')
        elif ordering == '-min_price':
            from django.db.models import Min
            queryset = queryset.annotate(min_detail_price=Min('details__price')).order_by('-min_detail_price')

        return queryset
    
    def list(self, request, *args, **kwargs):
        """Validate query parameters before executing list endpoint."""
        try:
            # Validate query parameters
            creator_id = request.query_params.get('creator_id')
            if creator_id:
                int(creator_id)
            
            min_price = request.query_params.get('min_price')
            if min_price:
                float(min_price)
            
            max_delivery_time = request.query_params.get('max_delivery_time')
            if max_delivery_time:
                int(max_delivery_time)
            
            ordering = request.query_params.get('ordering')
            if ordering and ordering not in ['updated_at', '-updated_at', 'min_price', '-min_price', 'created_at', '-created_at']:
                return Response(
                    {"error": "Invalid ordering field. Allowed: updated_at, created_at, min_price"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            page_size = request.query_params.get('page_size')
            if page_size:
                page_size_int = int(page_size)
                if page_size_int < 1:
                    return Response(
                        {"error": "page_size must be positive"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            return super().list(request, *args, **kwargs)
            
        except ValueError:
            return Response(
                {"error": "Invalid parameter format"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def create(self, request, *args, **kwargs):
        """Create offer only for authenticated business users."""
        try:
            profile = Profile.objects.get(user=request.user)
            if profile.type != 'business':
                return Response(
                    {"error": "Only business users can create offers"},
                    status=status.HTTP_403_FORBIDDEN
                )
        except Profile.DoesNotExist:
            return Response(
                {"error": "User profile not found"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            offer = serializer.save()
            # Return full detail objects in create response.
            response_serializer = OfferResponseWithFullDetailsSerializer(offer, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """Use default update behavior with permission checks."""
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Use default destroy behavior with permission checks."""
        return super().destroy(request, *args, **kwargs)


class OfferDetailViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only endpoint for offer detail resources."""
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.IsAuthenticated]