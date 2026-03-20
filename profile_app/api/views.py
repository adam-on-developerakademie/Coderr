from rest_framework import status
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotFound
from django.contrib.auth.models import User
from profile_app.models import Profile
from profile_app.api.filters import get_business_profiles_queryset, get_customer_profiles_queryset
from profile_app.api.permissions import IsProfileOwnerOrReadOnly
from .serializers import ProfileSerializer, BusinessProfileSerializer, CustomerProfileSerializer


class ProfileViewSet(ModelViewSet):
    """Profile endpoint for retrieve and partial update operations."""
    
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsProfileOwnerOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_object(self):
        """Load profile by user ID from URL parameter.
        # Run object-level permission checks.
        """
        user_id = self.kwargs.get('pk')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound("User profile was not found.")
            
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            raise NotFound("User profile was not found.")
        
        self.check_object_permissions(self.request, profile)
        
        return profile
    
    def retrieve(self, request, *args, **kwargs):
        """Return profile details for GET /api/profile/{pk}/."""
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """Update profile fields (including optional image upload).
        # Keep old file reference for safe replacement cleanup.
        # Save profile updates.
        # Delete replaced image file when a new one is uploaded.
        # Provide upload-specific help when image validation fails.
        """
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            try:
                old_file = profile.file

                updated_profile = serializer.save()

                if old_file and 'file' in request.data and old_file != updated_profile.file:
                    try:
                        old_file.delete(save=False)
                    except Exception:
                        pass
                
                return Response(serializer.data, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response(
                    {
                        'error': 'Failed to save profile.',
                        'details': str(e)
                    }, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            errors = serializer.errors
            if 'file' in errors:
                errors['file_help'] = (
                    "The 'file' field accepts image uploads. "
                    "Supported formats: .jpg, .jpeg, .png, .gif, .webp. "
                    "Use multipart/form-data for file uploads."
                )
            
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request, *args, **kwargs):
        """Disable list endpoint for the profile resource."""
        return Response(
            {'error': 'Endpoint not available'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def create(self, request, *args, **kwargs):
        """Disable profile creation (profiles are created at registration)."""
        return Response(
            {'error': 'Endpoint not available'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    
    def destroy(self, request, *args, **kwargs):
        """Disable profile deletion endpoint."""
        return Response(
            {'error': 'Endpoint not available'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class BusinessProfileViewSet(ReadOnlyModelViewSet):
    """Read-only list endpoint for business profiles."""
    
    serializer_class = BusinessProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only business profiles."""
        return get_business_profiles_queryset()
    
    def list(self, request, *args, **kwargs):
        """Return all business profiles for GET /api/profiles/business/."""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, *args, **kwargs):
        """Disable detail endpoint; list view only."""
        return Response(
            {'error': 'Endpoint not available'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )


class CustomerProfileViewSet(ReadOnlyModelViewSet):
    """Read-only list endpoint for customer profiles."""
    
    serializer_class = CustomerProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only customer profiles."""
        return get_customer_profiles_queryset()
    
    def list(self, request, *args, **kwargs):
        """Return all customer profiles for GET /api/profiles/customer/."""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Internal server error'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, *args, **kwargs):
        """Disable detail endpoint; list view only."""
        return Response(
            {'error': 'Endpoint not available'}, 
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
