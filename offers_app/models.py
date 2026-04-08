from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Offer(models.Model):
    """Offer model representing a business service listing."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offer_images/', blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Delete replaced image file to avoid orphaned media files."""
        old_image = None
        if self.pk:
            try:
                old_image = Offer.objects.get(pk=self.pk).image
            except Offer.DoesNotExist:
                old_image = None

        super().save(*args, **kwargs)

        if old_image and old_image != self.image:
            old_image.delete(save=False)

    def delete(self, *args, **kwargs):
        """Delete image file when offer is deleted."""
        image_file = self.image
        super().delete(*args, **kwargs)
        if image_file:
            image_file.delete(save=False)
    
    @property
    def min_price(self):
        """Return the minimum price across all offer details."""
        details = self.details.all()
        if details:
            return min(detail.price for detail in details)
        return 0
    
    @property
    def min_delivery_time(self):
        """Return the shortest delivery time across all offer details."""
        details = self.details.all()
        if details:
            return min(detail.delivery_time_in_days for detail in details)
        return 0
    
    class Meta:
        ordering = ['-updated_at']

class OfferDetail(models.Model):
    """Offer detail model for basic, standard, and premium packages."""
    OFFER_TYPE_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]
    
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=255)
    revisions = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    delivery_time_in_days = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    features = models.JSONField(default=list)
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)
    
    def __str__(self):
        return f"{self.offer.title} - {self.get_offer_type_display()}"
    
    class Meta:
        ordering = ['offer_type']
        unique_together = ['offer', 'offer_type']
