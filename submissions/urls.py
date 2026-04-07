from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PublicSubmissionViewSet, me

router = DefaultRouter()
router.register('submissions', PublicSubmissionViewSet, basename='submission')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', me),
]
