from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
	"""Review created by a customer user for a business user."""

	business_user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name="business_reviews",
	)
	reviewer = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name="written_reviews",
	)
	rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
	description = models.TextField(blank=True, default="")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-updated_at"]
		constraints = [
			models.UniqueConstraint(
				fields=["business_user", "reviewer"],
				name="unique_review_per_business_and_reviewer",
			)
		]

	def __str__(self):
		return f"Review #{self.id} ({self.reviewer_id} -> {self.business_user_id})"
