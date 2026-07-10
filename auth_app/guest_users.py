from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from profile_app.models import Profile


GUEST_LOGINS = {
    'customer': {
        'username': 'andrey',
        'password': 'Andrey-123456789',
    },
    'business': {
        'username': 'kevin',
        'password': 'Kevin-123456789',
    },
}


def _ensure_user(role, credentials):
    """Create or repair a deterministic guest user account."""
    email = f"{credentials['username']}@guest.local"
    user, _ = User.objects.get_or_create(username=credentials['username'], defaults={'email': email})
    user.email = email
    user.is_active = True
    user.is_staff = False
    user.is_superuser = False
    user.set_password(credentials['password'])
    user.save()
    return user


def _ensure_profile(user, role):
    """Ensure each guest user has a matching profile type."""
    Profile.objects.update_or_create(user=user, defaults={'type': role})


def _ensure_token(user):
    """Ensure each guest user has an API token for authenticated calls."""
    Token.objects.get_or_create(user=user)


def ensure_guest_users():
    """Create fixed guest users for local/demo environments."""
    # Keep this loop idempotent so repeated migrate runs are safe.
    for role, credentials in GUEST_LOGINS.items():
        user = _ensure_user(role, credentials)
        _ensure_profile(user, role)
        _ensure_token(user)