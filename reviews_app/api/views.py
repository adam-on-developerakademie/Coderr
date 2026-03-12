from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response

from profile_app.models import Profile
from reviews_app.api.serializers import ReviewSerializer
from reviews_app.models import Review


class IsReviewerOrReadOnly(permissions.BasePermission):
    """Only the reviewer may perform PATCH/DELETE operations."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return obj.reviewer == request.user


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for GET/POST/PATCH/DELETE review operations."""

    queryset = Review.objects.all().select_related("business_user", "reviewer")
    serializer_class = ReviewSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated, IsReviewerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["business_user", "reviewer"]
    ordering_fields = ["updated_at", "rating"]
    ordering = ["-updated_at"]

    def get_queryset(self):
        queryset = super().get_queryset()

        business_user_id = self.request.query_params.get("business_user_id")
        reviewer_id = self.request.query_params.get("reviewer_id")

        if business_user_id:
            queryset = queryset.filter(business_user_id=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer_id=reviewer_id)

        return queryset

    def create(self, request, *args, **kwargs):
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(
                {"detail": "Only authenticated users with a customer profile can create reviews."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if profile.type != "customer":
            return Response(
                {"detail": "Only authenticated users with a customer profile can create reviews."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        business_user_id = request.data.get("business_user")
        if business_user_id and Review.objects.filter(
            business_user_id=business_user_id,
            reviewer=request.user,
        ).exists():
            return Response(
                {"detail": "Only one review per business profile is allowed."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(reviewer=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)