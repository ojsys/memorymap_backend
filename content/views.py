from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response

from .models import SiteContent
from .serializers import SiteContentSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def content_dict(request):
    """Public — return all content as a flat {key: value} dict."""
    qs = SiteContent.objects.all()
    return Response({obj.key: obj.value for obj in qs})


@api_view(['GET'])
@permission_classes([IsAdminUser])
def content_list(request):
    """Admin — return full objects grouped by section."""
    qs = SiteContent.objects.all()
    grouped = {}
    for obj in qs:
        grouped.setdefault(obj.section, []).append(SiteContentSerializer(obj).data)
    return Response(grouped)


@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def content_update(request, key):
    """Admin — update a single content item by key."""
    try:
        obj = SiteContent.objects.get(key=key)
    except SiteContent.DoesNotExist:
        return Response({'error': 'Key not found.'}, status=status.HTTP_404_NOT_FOUND)

    value = request.data.get('value')
    if value is None:
        return Response({'error': '`value` is required.'}, status=status.HTTP_400_BAD_REQUEST)

    obj.value = value
    obj.save(update_fields=['value', 'updated_at'])
    return Response(SiteContentSerializer(obj).data)
