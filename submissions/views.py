from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response

from victims.models import Victim, ConsentStatus, Gender
from .models import PublicSubmission, SubmissionStatus
from .serializers import (
    PublicSubmissionCreateSerializer,
    PublicSubmissionAdminSerializer,
    PublicSubmissionListSerializer,
)


# ── /api/me/ — current user info including role ────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    groups = list(user.groups.values_list('name', flat=True))
    return Response({
        'id':           user.id,
        'username':     user.username,
        'full_name':    user.get_full_name(),
        'is_superuser': user.is_superuser,
        'is_staff':     user.is_staff,
        'groups':       groups,
        'is_cvt':       'CVT' in groups and not user.is_superuser,
    })


# ── Submission ViewSet ─────────────────────────────────────────────────────

class PublicSubmissionViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = PublicSubmission.objects.all()
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return PublicSubmissionCreateSerializer
        if self.action == 'list':
            return PublicSubmissionListSerializer
        return PublicSubmissionAdminSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ip = (
            request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
            or request.META.get('REMOTE_ADDR')
        )
        serializer.save(ip_address=ip)
        return Response(
            {'message': 'Thank you. Your submission has been received and will be reviewed by the community verification team.'},
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Auto-transition SUBMITTED → UNDER_REVIEW when a CVT/admin opens it
        if instance.status == SubmissionStatus.SUBMITTED:
            instance.status = SubmissionStatus.UNDER_REVIEW
            instance.save(update_fields=['status'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        submission = self.get_object()
        if submission.status == SubmissionStatus.APPROVED:
            return Response({'error': 'Already approved.'}, status=status.HTTP_400_BAD_REQUEST)

        # Determine consent status
        consent = ConsentStatus.CONSENTED if submission.submitter_consents else ConsentStatus.PENDING

        # Determine gender
        gender_map = {'M': Gender.MALE, 'F': Gender.FEMALE, 'NR': Gender.NOT_RECORDED}
        gender = gender_map.get(submission.victim_gender, Gender.NOT_RECORDED)

        victim = Victim.objects.create(
            full_name         = submission.victim_name or 'Name Withheld',
            age_at_death      = submission.victim_age,
            gender            = gender,
            community_ward    = submission.community_ward,
            year_of_death     = submission.year_of_death,
            cause_of_death    = submission.cause_of_death,
            biographical_note = submission.story,
            home_lat          = submission.home_lat,
            home_lng          = submission.home_lng,
            source            = f'Community submission — {submission.submitter_relationship or "anonymous"}',
            consent_status    = consent,
            added_by          = request.user,
        )

        submission.status      = SubmissionStatus.APPROVED
        submission.reviewed_by = request.user
        submission.reviewed_at = timezone.now()
        submission.review_notes = request.data.get('review_notes', '')
        submission.victim      = victim
        submission.save()

        return Response({'message': 'Approved. Victim record created.', 'victim_id': victim.id})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        submission = self.get_object()
        if submission.status == SubmissionStatus.APPROVED:
            return Response({'error': 'Cannot reject an already approved submission.'}, status=status.HTTP_400_BAD_REQUEST)

        submission.status       = SubmissionStatus.REJECTED
        submission.reviewed_by  = request.user
        submission.reviewed_at  = timezone.now()
        submission.review_notes = request.data.get('review_notes', '')
        submission.save()
        return Response({'message': 'Submission rejected.'})

    @action(detail=True, methods=['post'], url_path='request-info')
    def request_info(self, request, pk=None):
        submission = self.get_object()
        submission.status       = SubmissionStatus.NEEDS_INFO
        submission.reviewed_by  = request.user
        submission.reviewed_at  = timezone.now()
        submission.review_notes = request.data.get('review_notes', '')
        submission.save()
        return Response({'message': 'Marked as needing more information.'})
