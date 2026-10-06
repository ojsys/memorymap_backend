from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .permissions import IsSuperUser
from .roles import ADMINISTRATOR, CVT_GROUP, get_role
from .serializers import StaffUserSerializer, ProfileSerializer, PasswordChangeSerializer


# ── /api/me/ — current user info including role ────────────────────────────

def me_payload(user):
    groups = list(user.groups.values_list('name', flat=True))
    return {
        'id':           user.id,
        'username':     user.username,
        'first_name':   user.first_name,
        'last_name':    user.last_name,
        'full_name':    user.get_full_name(),
        'email':        user.email,
        'role':         get_role(user),
        'is_superuser': user.is_superuser,
        'is_staff':     user.is_staff,
        'groups':       groups,
        'is_cvt':       CVT_GROUP in groups and not user.is_superuser,
    }


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def me(request):
    if request.method == 'PATCH':
        s = ProfileSerializer(request.user, data=request.data, partial=True)
        s.is_valid(raise_exception=True)
        s.save()
    return Response(me_payload(request.user))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    s = PasswordChangeSerializer(data=request.data, context={'request': request})
    s.is_valid(raise_exception=True)
    request.user.set_password(s.validated_data['new_password'])
    request.user.save()
    return Response({'message': 'Password changed.'})


# ── /api/staff/users/ — staff management (administrators only) ─────────────

class StaffUserViewSet(viewsets.ModelViewSet):
    """
    Staff accounts are deactivated rather than deleted: victims.added_by
    is PROTECT, and an audit trail of who entered what must survive.
    """
    serializer_class   = StaffUserSerializer
    permission_classes = [IsSuperUser]
    http_method_names  = ['get', 'post', 'patch', 'head', 'options']
    pagination_class   = None

    def get_queryset(self):
        qs = User.objects.filter(is_staff=True).prefetch_related('groups').order_by('-is_active', 'username')
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(username__icontains=search) | Q(first_name__icontains=search) |
                Q(last_name__icontains=search) | Q(email__icontains=search)
            )
        return qs

    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        # Guard against an administrator locking themselves out.
        if user == request.user:
            if request.data.get('is_active') is False:
                return Response({'error': 'You cannot deactivate your own account.'},
                                status=status.HTTP_400_BAD_REQUEST)
            if 'role' in request.data and request.data['role'] != ADMINISTRATOR:
                return Response({'error': 'You cannot remove your own Administrator role.'},
                                status=status.HTTP_400_BAD_REQUEST)
        return super().partial_update(request, *args, **kwargs)
