from rest_framework.routers import DefaultRouter
from .views import VictimViewSet

router = DefaultRouter()
router.register('victims', VictimViewSet, basename='victim')

urlpatterns = router.urls
