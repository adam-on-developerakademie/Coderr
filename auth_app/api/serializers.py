from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from auth_app.api.filters import email_exists, username_exists
from profile_app.models import Profile


class RegistrationSerializer(serializers.Serializer):
    """Serializer used for user registration."""
    
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    repeated_password = serializers.CharField(min_length=6, write_only=True)
    type = serializers.ChoiceField(choices=Profile.TYPE_CHOICES)
    
    def validate(self, attrs):
        """Validate registration payload.
        # Password confirmation must match.
        # Username must be unique.
        # Email must be unique.
        """
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError("Passwords do not match.")

        if username_exists(attrs['username']):
            raise serializers.ValidationError("This username is already in use.")

        if email_exists(attrs['email']):
            raise serializers.ValidationError("This email address is already in use.")
        
        return attrs
    
    def create(self, validated_data):
        """Create user, profile, and token.
        # Remove confirmation field before creating user.
        # Create user account.
        # Create profile.
        # Create authentication token.
        """
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        profile = Profile.objects.create(
            user=user,
            type=user_type
        )

        token, created = Token.objects.get_or_create(user=user)
        
        return {
            'user': user,
            'profile': profile,
            'token': token
        }


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data in API responses."""
    
    type = serializers.CharField(source='profile.type', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'type']


class LoginSerializer(serializers.Serializer):
    """Serializer used for user login."""
    
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Validate login payload and authenticate user.
        # Authenticate user credentials.
        """
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")
        
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError("Invalid login credentials.")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        
        attrs['user'] = user
        return attrs
    
    def create(self, validated_data):
        """Create or fetch token for authenticated user.
        # Create or fetch token.
        """
        user = validated_data['user']

        token, created = Token.objects.get_or_create(user=user)
        
        return {
            'user': user,
            'token': token
        }