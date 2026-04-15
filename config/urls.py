from django.contrib import admin
from django.urls import path, include

admin.site.site_header  = 'Middle Belt Memorial'
admin.site.site_title   = 'MBM Admin'
admin.site.index_title  = 'Dashboard'
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from config.views import api_landing_page, redirect_to_frontend

urlpatterns = [
    path('', api_landing_page, name='api_landing_page'),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('victims.urls')),
    path('api/', include('oral_histories.urls')),
    path('api/', include('initiatives.urls')),
    path('api/', include('imports.urls')),
    path('api/', include('submissions.urls')),
    path('api/', include('content.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
