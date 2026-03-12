from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class Order(models.Model):
    """Order model linking customer and business users to an offer detail snapshot."""
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='customer_orders'
    )
    business_user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='business_orders'
    )
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    delivery_time_in_days = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.title} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']
