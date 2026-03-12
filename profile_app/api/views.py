from rest_framework import status
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotFound, PermissionDenied
from django.contrib.auth.models import User
from profile_app.models import Profile
from .serializers import ProfileSerializer, BusinessProfileSerializer, CustomerProfileSerializer


class IsProfileOwnerOrReadOnly(BasePermission):
    """Allow authenticated access and restrict write access to profile owners."""
    
    def has_permission(self, request, view):
        # Authentication is required for all profile endpoints.
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Read access for authenticated users.
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True

        # Write access only for the owner.
        return obj.user == request.user


class ProfileViewSet(ModelViewSet):
    """Profile endpoint for retrieve and partial update operations."""
    
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsProfileOwnerOrReadOnly]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_object(self):
        """Load profile by user ID from URL parameter."""
        user_id = self.kwargs.get('pk')
        
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound("User profile was not found.")
            
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            raise NotFound("User profile was not found.")
        
        # Run object-level permission checks.
        self.check_object_permissions(self.request, profile)
        
        return profile
    
    def retrieve(self, request, *args, **kwargs):
        """Return profile details for GET /api/profile/{pk}/."""
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def update(self, request, *args, **kwargs):
        """Update profile fields (including optional image upload)."""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            try:
                # Keep old file reference for safe replacement cleanup.
                old_file = profile.file
                
                # Save profile updates.
                updated_profile = serializer.save()
                
                # Delete replaced image file when a new one is uploaded.
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
            # Provide upload-specific help when image validation fails.
            errors = serializer.errors
            if 'file' in errors:
                errors['file_help'] = (
                    "The 'file' field accepts image uploads. "
                    "Supported formats: .jpg, .jpeg, .png, .gif, .webp. "
                    "Use multipart/form-data for file uploads."
                )
            
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
    
    def check_object_permissions(self, request, obj):
        """Override object permission check to return explicit 403 messages."""
        for permission in self.get_permissions():
            if not permission.has_object_permission(request, self, obj):
                # Any access to foreign profiles is forbidden.
                if obj.user != request.user:
                    raise PermissionDenied(
                        f"You are not allowed to access profile data for user {obj.user.username}. "
                        f"You may only edit your own profile (user ID: {request.user.id})."
                    )
                else:
                    raise PermissionDenied("You are not allowed to access this profile.")
    
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
        return Profile.objects.filter(type='business')
    
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
        return Profile.objects.filter(type='customer')
    
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
