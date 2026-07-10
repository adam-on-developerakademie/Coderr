from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_guest_users(sender, **kwargs):
    """Create fixed guest users after migrations have completed."""
    # Import lazily to avoid touching ORM models during app loading.
    from auth_app.guest_users import ensure_guest_users

    ensure_guest_users()


class AuthAppConfig(AppConfig):
    name = 'auth_app'
    verbose_name = 'Authentication'

    def ready(self):
        """Register startup signal handlers for this app."""
        # Keep signal registration idempotent across reloads.
        post_migrate.connect(
            create_guest_users,
            sender=self,
            dispatch_uid='auth_app.create_guest_users',
        )