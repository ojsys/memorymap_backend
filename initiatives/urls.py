from rest_framework.routers import DefaultRouter
from .views import CommunityInitiativeViewSet

router = DefaultRouter()
router.register('initiatives', CommunityInitiativeViewSet, basename='initiative')

urlpatterns = router.urls
