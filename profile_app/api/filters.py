from profile_app.models import Profile


def get_business_profiles_queryset():
    """Return queryset containing only business profiles."""
    return Profile.objects.filter(type='business')


def get_customer_profiles_queryset():
    """Return queryset containing only customer profiles."""
    return Profile.objects.filter(type='customer')
