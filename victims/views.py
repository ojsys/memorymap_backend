from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly, BasePermission
from rest_framework.response import Response
from django.db.models import Q, Count, Exists, OuterRef
import csv
import io


class IsSuperUser(BasePermission):
    """Only Django superusers may delete records."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

from .models import Victim, ConsentStatus
from .serializers import (
    VictimListSerializer,
    VictimDetailSerializer,
    VictimWriteSerializer,
    VictimGeoJSONSerializer,
)

# Year ranges shown in sidebar (label → list of years)
YEAR_RANGES = {
    '2001':      [2001],
    '2008-2010': [2008, 2009, 2010],
    '2011-2020': list(range(2011, 2021)),
    '2021-2024': list(range(2021, 2025)),
}


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
    ordering = ['-year_of_death']

    def get_queryset(self):
        from oral_histories.models import OralHistory

        if self.request.user and self.request.user.is_staff:
            qs = Victim.objects.all()
        else:
            qs = public_victims_qs()

        # Annotate with has_oral_history to avoid N+1 in serializer
        qs = qs.annotate(
            has_oral_history=Exists(OralHistory.objects.filter(victim=OuterRef('pk')))
        )

        params = self.request.query_params

        # Gender filter (comma-separated: M,F,NR)
        genders = params.get('genders')
        if genders:
            qs = qs.filter(gender__in=genders.split(','))

        # Year filter (comma-separated individual years)
        years = params.get('years')
        if years:
            year_list = [y.strip() for y in years.split(',') if y.strip().isdigit()]
            qs = qs.filter(year_of_death__in=year_list)

        # Ward filter (comma-separated exact matches)
        wards = params.get('wards')
        if wards:
            qs = qs.filter(community_ward__in=wards.split(','))

        # Location mapped filter
        if params.get('location_mapped') == 'true':
            qs = qs.filter(
                Q(home_lat__isnull=False) |
                Q(incident_lat__isnull=False) |
                Q(burial_lat__isnull=False)
            )

        # Has oral history filter
        if params.get('has_oral_history') == 'true':
            qs = qs.filter(has_oral_history=True)

        # Direct consent_status filter (staff only — used by admin panel)
        if self.request.user and self.request.user.is_staff:
            consent_status = params.get('consent_status')
            if consent_status:
                qs = qs.filter(consent_status=consent_status)

        # Consent type filter (for public: CONSENTED and/or ANONYMOUS)
        consent_types = params.get('consent_types')
        if consent_types:
            allowed = [
                t for t in consent_types.split(',')
                if t in [ConsentStatus.CONSENTED, ConsentStatus.ANONYMOUS]
            ]
            if allowed:
                qs = qs.filter(consent_status__in=allowed)

        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return VictimListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return VictimWriteSerializer
        return VictimDetailSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsSuperUser()]
        if self.action in ['create', 'update', 'partial_update']:
            return [IsAdminUser()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        """Aggregate stats for the register sidebar and homepage."""
        from oral_histories.models import OralHistory

        qs = public_victims_qs()
        total = qs.count()

        mapped_q = Q(home_lat__isnull=False) | Q(incident_lat__isnull=False) | Q(burial_lat__isnull=False)

        oral_histories_count = OralHistory.objects.filter(
            victim__consent_status__in=[ConsentStatus.CONSENTED, ConsentStatus.ANONYMOUS]
        ).count()

        locations_mapped = qs.filter(mapped_q).count()

        # Gender counts
        gender_counts = {}
        for row in qs.values('gender').annotate(n=Count('id')):
            gender_counts[row['gender']] = row['n']

        # Year range counts
        year_range_counts = {}
        for label, years in YEAR_RANGES.items():
            year_range_counts[label] = qs.filter(year_of_death__in=years).count()

        # Top wards (top 10 by count)
        top_wards = list(
            qs.values('community_ward')
            .annotate(n=Count('id'))
            .order_by('-n')[:10]
        )

        # Record type counts
        record_type_counts = {
            'has_oral_history': OralHistory.objects.filter(
                victim__consent_status__in=[ConsentStatus.CONSENTED, ConsentStatus.ANONYMOUS]
            ).values('victim').distinct().count(),
            'location_mapped': locations_mapped,
            'named_consented': qs.filter(consent_status=ConsentStatus.CONSENTED).count(),
            'anonymous': qs.filter(consent_status=ConsentStatus.ANONYMOUS).count(),
        }

        return Response({
            'total': total,
            'oral_histories': oral_histories_count,
            'locations_mapped': locations_mapped,
            'gender_counts': gender_counts,
            'year_range_counts': year_range_counts,
            'top_wards': top_wards,
            'record_type_counts': record_type_counts,
        })

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
