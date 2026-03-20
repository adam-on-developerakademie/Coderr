import django_filters

from reviews_app.models import Review


class ReviewFilter(django_filters.FilterSet):
    business_user_id = django_filters.NumberFilter(field_name='business_user_id')
    reviewer_id = django_filters.NumberFilter(field_name='reviewer_id')

    class Meta:
        model = Review
        fields = ['business_user_id', 'reviewer_id']


def review_exists_for_business_and_reviewer(business_user_id, reviewer):
    """Return whether a reviewer already created a review for a business user."""
    return Review.objects.filter(
        business_user_id=business_user_id,
        reviewer=reviewer,
    ).exists()
