from django import template

register = template.Library()


@register.simple_tag
def admin_stats():
    from victims.models import Victim, ConsentStatus
    from submissions.models import PublicSubmission, SubmissionStatus
    from imports.models import BulkImport
    from oral_histories.models import OralHistory
    from initiatives.models import CommunityInitiative

    return {
        'total_victims':        Victim.objects.count(),
        'consented':            Victim.objects.filter(consent_status=ConsentStatus.CONSENTED).count(),
        'anonymous':            Victim.objects.filter(consent_status=ConsentStatus.ANONYMOUS).count(),
        'pending_consent':      Victim.objects.filter(consent_status=ConsentStatus.PENDING).count(),
        'oral_histories':       OralHistory.objects.count(),
        'initiatives':          CommunityInitiative.objects.count(),
        'pending_submissions':  PublicSubmission.objects.filter(status=SubmissionStatus.SUBMITTED).count(),
        'under_review':         PublicSubmission.objects.filter(status=SubmissionStatus.UNDER_REVIEW).count(),
        'pending_imports':      BulkImport.objects.filter(status='PENDING').count(),
    }


@register.simple_tag
def recent_submissions(count=8):
    from submissions.models import PublicSubmission
    return PublicSubmission.objects.select_related('reviewed_by').order_by('-created_at')[:count]


@register.simple_tag
def recent_victims(count=6):
    from victims.models import Victim
    return Victim.objects.order_by('-created_at')[:count]
