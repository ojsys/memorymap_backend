from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.db.models import Q
import csv
import io

from .models import Victim, ConsentStatus
from .serializers import (
    VictimListSerializer,
    VictimDetailSerializer,
    VictimWriteSerializer,
    VictimGeoJSONSerializer,
)


def public_victims_qs():
    """Only records visible to the public."""
    return Victim.objects.filter(
        consent_status__in=[ConsentStatus.CONSENTED, ConsentStatus.ANONYMOUS]
    )


class VictimViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'biographical_note', 'community_ward']
    ordering_fields = ['year_of_death', 'full_name', 'created_at']

    def get_queryset(self):
        if self.request.user and self.request.user.is_staff:
            qs = Victim.objects.all()
        else:
            qs = public_victims_qs()

        gender = self.request.query_params.get('gender')
        if gender:
            qs = qs.filter(gender=gender)

        year = self.request.query_params.get('year')
        if year:
            qs = qs.filter(Q(year_of_death=year) | Q(date_of_death__year=year))

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return VictimListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return VictimWriteSerializer
        return VictimDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='geojson')
    def geojson(self, request):
        """GeoJSON endpoint consumed by Leaflet."""
        qs = public_victims_qs()
        serializer = VictimGeoJSONSerializer(qs, many=True, context={'request': request})
        features = []
        for victim in serializer.data:
            location_types = [
                ('home', victim.get('home_lat'), victim.get('home_lng')),
                ('incident', victim.get('incident_lat'), victim.get('incident_lng')),
                ('burial', victim.get('burial_lat'), victim.get('burial_lng')),
            ]
            for loc_type, lat, lng in location_types:
                if lat is not None and lng is not None:
                    features.append({
                        'type': 'Feature',
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [float(lng), float(lat)],
                        },
                        'properties': {
                            'id': victim['id'],
                            'name': victim['display_name'],
                            'year': victim['effective_year'],
                            'gender': victim['gender'],
                            'community_ward': victim['community_ward'],
                            'location_type': loc_type,
                        },
                    })
        return Response({'type': 'FeatureCollection', 'features': features})

    @action(detail=False, methods=['post'], url_path='import/csv', permission_classes=[IsAdminUser])
    def import_csv(self, request):
        """Bulk import victims from CSV upload."""
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        decoded = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        created, errors = [], []

        for i, row in enumerate(reader, start=2):
            serializer = VictimWriteSerializer(data=row, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                created.append(i)
            else:
                errors.append({'row': i, 'errors': serializer.errors})

        return Response(
            {'created': len(created), 'errors': errors},
            status=status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED,
        )
