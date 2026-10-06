from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StaffUserViewSet, me, change_password

router = DefaultRouter()
router.register('staff/users', StaffUserViewSet, basename='staff-user')

urlpatterns = [
    path('', include(router.urls)),
    path('me/', me),
    path('me/password/', change_password),
]
