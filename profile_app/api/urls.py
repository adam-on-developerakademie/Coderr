from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileViewSet, BusinessProfileViewSet, CustomerProfileViewSet

# Router für ViewSets
router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'profiles/business', BusinessProfileViewSet, basename='business-profile')
router.register(r'profiles/customer', CustomerProfileViewSet, basename='customer-profile')

urlpatterns = [
    path('', include(router.urls)),
]