from rest_framework import serializers
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for review read/write operations."""

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "reviewer", "created_at", "updated_at"]

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.method in ["PATCH", "PUT"]:
            allowed_fields = {"rating", "description"}
            request_fields = set(self.initial_data.keys())
            disallowed_fields = request_fields - allowed_fields
            if disallowed_fields:
                raise serializers.ValidationError(
                    f"Only these fields are editable: rating, description. Invalid: {', '.join(sorted(disallowed_fields))}"
                )
        return attrs