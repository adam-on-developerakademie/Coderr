from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db.models import Avg

from core.pagination import StandardPagination

from reviews_app.models import Review
from offers_app.models import Offer
from baseinfo_app.api.serializers import BaseInfoSerializer
from baseinfo_app.api.permissions import PublicBaseInfoPermission
from baseinfo_app.api.filters import get_business_profile_count


class BaseInfoViewSet(viewsets.ModelViewSet):
    """Return platform-level aggregate statistics for GET /api/base-info/.
    # ModelViewSet requires a queryset, although this endpoint is aggregate-only.
    # Read-only endpoint.
    """
    serializer_class = BaseInfoSerializer
    pagination_class = StandardPagination
    permission_classes = [PublicBaseInfoPermission]
    authentication_classes = []
    queryset = Offer.objects.none()
    http_method_names = ['get', 'head', 'options']

    def list(self, request, *args, **kwargs):
        try:
            review_count = Review.objects.count()

            avg_result = Review.objects.aggregate(avg=Avg('rating'))['avg']
            average_rating = round(float(avg_result), 1) if avg_result is not None else 0.0

            business_profile_count = get_business_profile_count()

            offer_count = Offer.objects.count()

            data = {
                'review_count': review_count,
                'average_rating': average_rating,
                'business_profile_count': business_profile_count,
                'offer_count': offer_count,
            }
            return Response(data, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {'error': 'Internal server error.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
