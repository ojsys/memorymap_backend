from rest_framework.routers import DefaultRouter
from .views import BulkImportViewSet

router = DefaultRouter()
router.register('imports', BulkImportViewSet, basename='import')

urlpatterns = router.urls
