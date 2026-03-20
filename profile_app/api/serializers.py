from rest_framework import serializers
from django.contrib.auth.models import User
from profile_app.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for full profile data including file upload support.
    # Additional fields mapped from Django's user model.
    # ImageField handles profile image uploads.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email')
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    type = serializers.ChoiceField(choices=Profile.TYPE_CHOICES, required=False)
    
    file = serializers.ImageField(
        required=False, 
        allow_null=True,
        help_text="Profile image upload. Supported formats: .jpg, .jpeg, .png, .gif, .webp"
    )
    
    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 
            'type', 'email', 'created_at'
        ]
        read_only_fields = ['user', 'username', 'created_at']
    
    def to_representation(self, instance):
        """Ensure nullable fields are returned as empty strings where required.
        # Keep these fields as non-null strings in the response contract.
        # Return empty string when no profile image is set.
        """
        data = super().to_representation(instance)

        empty_string_fields = ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        
        for field in empty_string_fields:
            if data.get(field) is None:
                data[field] = ''
        
        if not instance.file:
            data['file'] = ""
        
        return data
    
    def update(self, instance, validated_data):
        """Update profile data and related user fields.
        # Extract user-specific fields from payload.
        # Update user email if included.
        # Update profile model fields.
        """
        user_data = validated_data.pop('user', {})

        if 'email' in user_data:
            instance.user.email = user_data['email']
            instance.user.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class BusinessProfileSerializer(serializers.ModelSerializer):
    """Serializer for business profile list response.
    # ImageField for profile image serialization.
    """
    
    username = serializers.CharField(source='user.username', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    file = serializers.ImageField(
        required=False, 
        allow_null=True,
        help_text="Profile image upload"
    )
    
    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type'
        ]
        read_only_fields = ['user', 'username', 'type']
    
    def to_representation(self, instance):
        """Ensure nullable fields are returned as empty strings where required.
        # Keep these fields as non-null strings in the response contract.
        # Return empty string when no profile image is set.
        """
        data = super().to_representation(instance)

        empty_string_fields = ['first_name', 'last_name', 'location', 'tel', 'description', 'working_hours']
        
        for field in empty_string_fields:
            if data.get(field) is None:
                data[field] = ''
        
        if not instance.file:
            data['file'] = ""
        
        return data


class CustomerProfileSerializer(serializers.ModelSerializer):
    """Serializer for customer profile list response."""
    
    username = serializers.CharField(source='user.username', read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    uploaded_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'user', 'username', 'first_name', 'last_name', 'file',
            'uploaded_at', 'type'
        ]
        read_only_fields = ['user', 'username', 'type', 'uploaded_at']
    
    def to_representation(self, instance):
        """Ensure nullable fields are returned as empty strings where required.
        # Keep these fields as non-null strings in the response contract.
        """
        data = super().to_representation(instance)

        empty_string_fields = ['first_name', 'last_name']
        
        for field in empty_string_fields:
            if data.get(field) is None:
                data[field] = ''
        
        return data