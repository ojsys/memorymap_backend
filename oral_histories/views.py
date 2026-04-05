from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from .models import OralHistory
from .serializers import OralHistorySerializer


class OralHistoryViewSet(viewsets.ModelViewSet):
    queryset = OralHistory.objects.select_related('victim').all()
    serializer_class = OralHistorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]
