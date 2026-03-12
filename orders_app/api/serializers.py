from rest_framework import serializers
from orders_app.models import Order
from offers_app.models import OfferDetail


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for order read responses."""
    
    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'created_at',
            'updated_at',
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating an order from offer_detail_id."""
    
    offer_detail_id = serializers.IntegerField(required=True)
    
    def validate_offer_detail_id(self, value):
        """Validate that offer_detail_id is an integer."""
        if not isinstance(value, int):
            raise serializers.ValidationError("offer_detail_id must be a number.")
        return value
    
    def create(self, validated_data):
        """Create a new order from the selected OfferDetail."""
        from rest_framework.exceptions import NotFound
        
        offer_detail_id = validated_data['offer_detail_id']
        
        # Raise 404 when OfferDetail does not exist.
        try:
            offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        except OfferDetail.DoesNotExist:
            raise NotFound("The specified offer detail was not found.")
        
        customer_user = self.context['request'].user
        business_user = offer_detail.offer.user
        
        order = Order.objects.create(
            customer_user=customer_user,
            business_user=business_user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status='in_progress',
        )
        
        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for status-only PATCH updates."""
    
    class Meta:
        model = Order
        fields = ['status']
    
    def validate(self, data):
        """Validate status update payload."""
        # Ensure that only status can be updated.
        allowed_fields = {'status'}
        request_fields = set(self.initial_data.keys())
        
        extra_fields = request_fields - allowed_fields
        if extra_fields:
            raise serializers.ValidationError(
                f"Invalid fields: {', '.join(extra_fields)}. Only 'status' can be updated."
            )
        
        # Validate status value against allowed states.
        if 'status' in data:
            valid_statuses = ['in_progress', 'completed', 'cancelled']
            if data['status'] not in valid_statuses:
                raise serializers.ValidationError({
                    'status': f"Invalid status. Allowed values: {', '.join(valid_statuses)}"
                })
        
        return data
    
    def update(self, instance, validated_data):
        """Update status field only."""
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
