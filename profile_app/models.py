from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """Profile model for users with business or customer type."""
    
    TYPE_CHOICES = [
        ('business', 'Business'),
        ('customer', 'Customer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')
    file = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, default='')
    tel = models.CharField(max_length=20, blank=True, default='')
    description = models.TextField(blank=True, default='')
    working_hours = models.CharField(max_length=100, blank=True, default='')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='customer')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.type}"

    class Meta:
        db_table = 'profile'
