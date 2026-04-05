from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from .models import CommunityInitiative
from .serializers import CommunityInitiativeSerializer


class CommunityInitiativeViewSet(viewsets.ModelViewSet):
    queryset = CommunityInitiative.objects.all()
    serializer_class = CommunityInitiativeSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]
