from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response

from core.pagination import StandardPagination

from offers_app.models import Offer, OfferDetail
from offers_app.api.filters import OfferFilter, OfferOrderingFilter, OfferQueryParamsValidationBackend
from offers_app.api.permissions import IsBusinessUserPermission, IsOwnerOrReadOnly, OfferCreatePermission
from offers_app.api.serializers import (
    OfferListSerializer, OfferDetailViewSerializer, OfferCreateUpdateSerializer,
    OfferDetailSerializer, OfferResponseWithFullDetailsSerializer
)


class OfferViewSet(viewsets.ModelViewSet):
    """ViewSet for offer CRUD operations."""
    queryset = Offer.objects.all()
    pagination_class = StandardPagination
    filter_backends = [
        OfferQueryParamsValidationBackend,
        DjangoFilterBackend,
        filters.SearchFilter,
        OfferOrderingFilter,
    ]
    filterset_class = OfferFilter
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'created_at', 'min_price']
    ordering = ['-updated_at']

    def get_permissions(self):
        """Apply endpoint-specific permissions according to the documented contract."""
        if self.action == 'list':
            return [permissions.AllowAny()]
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated()]
        return [IsBusinessUserPermission(), IsOwnerOrReadOnly()]

    def perform_authentication(self, request):
        """Skip authentication for public list endpoint to avoid 401 on invalid auth headers."""
        if self.action == 'list':
            return
        super().perform_authentication(request)
    
    def get_serializer_class(self):
        """
        Return different serializers for different actions.
        # retrieve
        """
        if self.action == 'list':
            return OfferListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return OfferCreateUpdateSerializer
        else:
            return OfferDetailViewSerializer
    
    def get_queryset(self):
        """Base queryset for offer listing and detail endpoints."""
        return Offer.objects.select_related('user').prefetch_related('details')
    
    def create(self, request, *args, **kwargs):
        """Create offer only for authenticated business users.
        # Return full detail objects in create response.
        """
        denied_response = OfferCreatePermission.denied_response_for_user(request.user)
        if denied_response is not None:
            return denied_response
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            offer = serializer.save()
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