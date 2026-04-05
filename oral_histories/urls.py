from rest_framework.routers import DefaultRouter
from .views import OralHistoryViewSet

router = DefaultRouter()
router.register('oral-histories', OralHistoryViewSet, basename='oral-history')

urlpatterns = router.urls
