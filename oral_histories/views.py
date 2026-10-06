from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from victims.models import ConsentStatus
from .models import OralHistory
from .serializers import OralHistorySerializer


class OralHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = OralHistorySerializer

    def get_queryset(self):
        qs = OralHistory.objects.select_related('victim')
        # Consent gate: the public never sees histories of PENDING victims
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(victim__consent_status__in=[ConsentStatus.CONSENTED, ConsentStatus.ANONYMOUS])
        victim = self.request.query_params.get('victim')
        if victim and victim.isdigit():
            qs = qs.filter(victim_id=victim)
        return qs

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]
