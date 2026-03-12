from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet

# Router für ViewSets
router = DefaultRouter()
router.register(r'', AuthViewSet, basename='auth')

urlpatterns = [
    #path("", include("rest_framework.urls")),
    path("", include(router.urls)),
]