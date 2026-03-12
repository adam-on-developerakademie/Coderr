from rest_framework.routers import DefaultRouter
from offers_app.api.views import OfferViewSet, OfferDetailViewSet

# Router für ViewSets - spezifische Pfade to avoid conflicts with auth_app
router = DefaultRouter()
router.register(r'offers', OfferViewSet, basename='offers')
router.register(r'offerdetails', OfferDetailViewSet, basename='offerdetails')

urlpatterns = router.urls