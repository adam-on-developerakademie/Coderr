from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from profile_app.models import Profile


class RegistrationSerializer(serializers.Serializer):
    """Serializer used for user registration."""
    
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    repeated_password = serializers.CharField(min_length=6, write_only=True)
    type = serializers.ChoiceField(choices=Profile.TYPE_CHOICES)
    
    def validate(self, attrs):
        """Validate registration payload."""
        
        # Password confirmation must match.
        if attrs['password'] != attrs['repeated_password']:
            raise serializers.ValidationError("Passwords do not match.")
        
        # Username must be unique.
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("This username is already in use.")
        
        # Email must be unique.
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("This email address is already in use.")
        
        return attrs
    
    def create(self, validated_data):
        """Create user, profile, and token."""
        
        # Remove confirmation field before creating user.
        validated_data.pop('repeated_password')
        user_type = validated_data.pop('type')
        
        # Create user account.
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Create profile.
        profile = Profile.objects.create(
            user=user,
            type=user_type
        )
        
        # Create authentication token.
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
        """Validate login payload and authenticate user."""
        username = attrs.get('username')
        password = attrs.get('password')
        
        if not username or not password:
            raise serializers.ValidationError("Username and password are required.")
        
        # Authenticate user credentials.
        user = authenticate(username=username, password=password)
        
        if not user:
            raise serializers.ValidationError("Invalid login credentials.")
        
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")
        
        attrs['user'] = user
        return attrs
    
    def create(self, validated_data):
        """Create or fetch token for authenticated user."""
        user = validated_data['user']
        
        # Create or fetch token.
        token, created = Token.objects.get_or_create(user=user)
        
        return {
            'user': user,
            'token': token
        }