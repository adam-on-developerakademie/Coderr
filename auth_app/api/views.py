from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth.models import User
from auth_app.api.permissions import AllowAnyAuthPermission
from .serializers import RegistrationSerializer, UserSerializer, LoginSerializer


class AuthViewSet(ModelViewSet):
    """ViewSet for registration and login endpoints."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAnyAuthPermission]
    
    def get_serializer_class(self):
        """Select serializer class based on the active action."""
        if self.action in ['register']:
            return RegistrationSerializer
        elif self.action in ['login']:
            return LoginSerializer
        return UserSerializer
    
    @action(detail=False, methods=['post'], url_path='registration')
    def register(self, request):
        """Handle user registration via POST /api/registration/.
        # Create user, profile, and authentication token.
        """
        
        serializer = RegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                result = serializer.save()
                user = result['user']
                token = result['token']
                
                response_data = {
                    'token': token.key,
                    'username': user.username,
                    'email': user.email,
                    'user_id': user.id,
                }
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            except Exception as e:
                return Response(
                    {'error': 'Internal server error during user registration.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        """Handle user login via POST /api/login/.
        # Authenticate user and return existing/new token.
        # Build response payload according to endpoint contract.
        """
        
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                result = serializer.save()
                user = result['user']
                token = result['token']

                response_data = {
                    'token': token.key,
                    'username': user.username,
                    'email': user.email,
                    'user_id': user.id
                }
                
                return Response(response_data, status=status.HTTP_200_OK)
            
            except Exception as e:
                return Response(
                    {'error': 'Internal server error during login.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
