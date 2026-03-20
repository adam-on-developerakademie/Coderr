from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response

from reviews_app.api.filters import ReviewFilter, review_exists_for_business_and_reviewer
from reviews_app.api.permissions import IsReviewerOrReadOnly, ReviewCreatePermission
from reviews_app.api.serializers import ReviewSerializer
from reviews_app.models import Review


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for GET/POST/PATCH/DELETE review operations."""

    queryset = Review.objects.all().select_related("business_user", "reviewer")
    serializer_class = ReviewSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated, IsReviewerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ["updated_at", "rating"]
    ordering = ["-updated_at"]

    def create(self, request, *args, **kwargs):
        denied_response = ReviewCreatePermission.denied_response_for_user(request.user)
        if denied_response is not None:
            return denied_response

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        business_user_id = request.data.get("business_user")
        if business_user_id and review_exists_for_business_and_reviewer(
            business_user_id,
            request.user,
        ):
            return Response(
                {"detail": "Only one review per business profile is allowed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save(reviewer=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)