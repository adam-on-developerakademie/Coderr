from rest_framework.routers import DefaultRouter
from baseinfo_app.api.views import BaseInfoViewSet

router = DefaultRouter()
router.register(r'base-info', BaseInfoViewSet, basename='base-info')

urlpatterns = router.urls
