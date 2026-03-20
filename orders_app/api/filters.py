from django.db.models import Q

from orders_app.models import Order
from profile_app.models import Profile


def get_orders_for_user(user):
    """Return orders where the user is customer or business user."""
    return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))


def business_profile_exists(user):
    """Return whether the given user has a business profile."""
    return Profile.objects.filter(user=user, type='business').exists()


def get_in_progress_order_count_for_business_user(user):
    """Return number of in-progress orders for the given business user."""
    return Order.objects.filter(business_user=user, status='in_progress').count()


def get_completed_order_count_for_business_user(user):
    """Return number of completed orders for the given business user."""
    return Order.objects.filter(business_user=user, status='completed').count()
