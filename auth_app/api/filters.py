from django.contrib.auth.models import User


def username_exists(username):
    """Return whether the given username already exists."""
    return User.objects.filter(username=username).exists()


def email_exists(email):
    """Return whether the given email already exists."""
    return User.objects.filter(email=email).exists()
