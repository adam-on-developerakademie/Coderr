from rest_framework import serializers
from django.contrib.auth.models import User
from offers_app.models import Offer, OfferDetail
from decimal import Decimal


class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializer for the OfferDetail model."""
    price = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'), coerce_to_string=False)

    class Meta:
        model = OfferDetail
        fields = [
            'id', 'title', 'revisions', 'delivery_time_in_days', 
            'price', 'features', 'offer_type'
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        price = representation.get('price')
        if isinstance(price, Decimal):
            representation['price'] = float(price)
        return representation


class OfferDetailUrlSerializer(serializers.ModelSerializer):
    """Serializer for offer detail references used in list/detail responses."""
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = OfferDetail
        fields = ['id', 'url']
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/offerdetails/{obj.id}/')
        return f'/api/offerdetails/{obj.id}/'


class UserDetailsSerializer(serializers.ModelSerializer):
    """Serializer for basic user identity fields in offer responses."""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']


class OfferListSerializer(serializers.ModelSerializer):
    """Serializer for GET /api/offers/ list responses."""
    details = OfferDetailUrlSerializer(many=True, read_only=True)
    min_price = serializers.ReadOnlyField()
    min_delivery_time = serializers.ReadOnlyField()
    user_details = UserDetailsSerializer(source='user', read_only=True)
    
    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description', 
            'created_at', 'updated_at', 'details', 
            'min_price', 'min_delivery_time', 'user_details'
        ]


class OfferDetailViewSerializer(serializers.ModelSerializer):
    """Serializer for GET/PATCH /api/offers/{id}/ responses."""
    details = OfferDetailUrlSerializer(many=True, read_only=True)
    min_price = serializers.ReadOnlyField()
    min_delivery_time = serializers.ReadOnlyField()
    
    class Meta:
        model = Offer
        fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at', 'details',
            'min_price', 'min_delivery_time'
        ]


class OfferResponseWithFullDetailsSerializer(serializers.ModelSerializer):
    """Serializer for create/update responses with fully expanded detail objects."""
    details = serializers.SerializerMethodField()
    
    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_details(self, obj):
        """Return full detail objects instead of URLs"""
        return OfferDetailSerializer(obj.details.all(), many=True).data


class OfferCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for offer create/update operations with nested details."""
    details = OfferDetailSerializer(many=True, required=False)
    
    class Meta:
        model = Offer
        fields = ['id', 'title', 'image', 'description', 'details', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        """Initialize serializer and adapt nested detail requirements for PATCH.
        # For PATCH, nested detail fields are optional except offer_type.
        """
        super().__init__(*args, **kwargs)

        if self.partial and 'details' in self.fields:
            detail_serializer = self.fields['details'].child
            for field_name, field in detail_serializer.fields.items():
                if field_name != 'offer_type':
                    field.required = False
    
    def validate_details(self, value):
        """Validate detail payload for create and partial update requests."""
        if self.partial:
            offer_types = [detail.get('offer_type') for detail in value]

            if any(not offer_type for offer_type in offer_types):
                raise serializers.ValidationError("For PATCH, each detail must include offer_type for identification.")

            if len(set(offer_types)) != len(offer_types):
                raise serializers.ValidationError("Each offer_type may appear only once.")

            if self.instance is not None:
                existing_types = set(self.instance.details.values_list('offer_type', flat=True))
                unknown_types = [offer_type for offer_type in offer_types if offer_type not in existing_types]
                if unknown_types:
                    raise serializers.ValidationError("Invalid offer_type for this offer.")

            return value

        if len(value) != 3:
            raise serializers.ValidationError("An offer must contain exactly 3 details.")
        
        offer_types = [detail.get('offer_type') for detail in value]
        required_types = ['basic', 'standard', 'premium']
        
        for required_type in required_types:
            if required_type not in offer_types:
                raise serializers.ValidationError(
                    f"Offer must include {', '.join(required_types)} details."
                )

        if len(set(offer_types)) != len(offer_types):
            raise serializers.ValidationError("Each offer_type may appear only once.")
        
        return value
    
    def create(self, validated_data):
        details_data = validated_data.pop('details', None)
        if details_data is None:
            raise serializers.ValidationError({'details': ['This field is required.']})
        validated_data['user'] = self.context['request'].user
        offer = Offer.objects.create(**validated_data)
        
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        
        return offer
    
    def update(self, instance, validated_data):
        """Update offer and detail objects.
        # Update offer fields.
        # Update detail objects if provided.
        # For full updates, all three package types must be present.
        """
        details_data = validated_data.pop('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            if self.partial:
                existing_details = {
                    detail.offer_type: detail
                    for detail in instance.details.all()
                }

                for detail_data in details_data:
                    offer_type = detail_data.get('offer_type')
                    detail_instance = existing_details.get(offer_type)

                    if detail_instance is None:
                        raise serializers.ValidationError("Invalid offer_type for this offer.")

                    for attr, value in detail_data.items():
                        if attr == 'offer_type':
                            continue
                        setattr(detail_instance, attr, value)
                    detail_instance.save()
            else:
                offer_types = [detail.get('offer_type') for detail in details_data]
                required_types = ['basic', 'standard', 'premium']

                for required_type in required_types:
                    if required_type not in offer_types:
                        raise serializers.ValidationError(
                            f"Offer must include {', '.join(required_types)} details."
                        )

                instance.details.all().delete()

                for detail_data in details_data:
                    OfferDetail.objects.create(offer=instance, **detail_data)
        
        return instance
    
    def to_representation(self, instance):
        """
        Return full offer details for response
        """
        return OfferResponseWithFullDetailsSerializer(instance, context=self.context).data