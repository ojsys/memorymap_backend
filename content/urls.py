from django.urls import path
from .views import content_dict, content_list, content_update

urlpatterns = [
    path('content/',        content_dict,   name='content-public'),
    path('content/admin/',  content_list,   name='content-admin'),
    path('content/<slug:key>/', content_update, name='content-update'),
]
