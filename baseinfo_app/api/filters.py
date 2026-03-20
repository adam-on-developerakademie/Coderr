from profile_app.models import Profile


def get_business_profile_count():
    """Return the number of business profiles."""
    return Profile.objects.filter(type='business').count()
