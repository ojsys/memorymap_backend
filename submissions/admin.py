from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.contrib import messages
from .models import PublicSubmission, SubmissionStatus
from victims.models import Victim, ConsentStatus, Gender


# ── Admin actions ────────────────────────────────────────────────────────────

@admin.action(description='Mark selected → Under Review')
def mark_under_review(modeladmin, request, queryset):
    updated = queryset.filter(
        status=SubmissionStatus.SUBMITTED
    ).update(status=SubmissionStatus.UNDER_REVIEW, reviewed_by=request.user)
    modeladmin.message_user(request, f'{updated} submission(s) marked as Under Review.')


@admin.action(description='Mark selected → Needs More Info')
def mark_needs_info(modeladmin, request, queryset):
    updated = queryset.update(status=SubmissionStatus.NEEDS_INFO, reviewed_by=request.user)
    modeladmin.message_user(request, f'{updated} submission(s) marked as Needs Info.')


@admin.action(description='Reject selected submissions')
def reject_submissions(modeladmin, request, queryset):
    updated = queryset.exclude(status=SubmissionStatus.APPROVED).update(
        status=SubmissionStatus.REJECTED,
        reviewed_by=request.user,
        reviewed_at=timezone.now(),
    )
    modeladmin.message_user(request, f'{updated} submission(s) rejected.', messages.WARNING)


@admin.action(description='Approve and create victim record(s)')
def approve_and_create(modeladmin, request, queryset):
    created = 0
    skipped = 0
    for sub in queryset.filter(status__in=[
        SubmissionStatus.SUBMITTED,
        SubmissionStatus.UNDER_REVIEW,
        SubmissionStatus.NEEDS_INFO,
    ]):
        if hasattr(sub, 'victim') and sub.victim:
            skipped += 1
            continue

        gender = sub.victim_gender if sub.victim_gender in ('M', 'F') else Gender.NOT_RECORDED
        victim = Victim.objects.create(
            full_name      = sub.victim_name or 'Name Withheld',
            age_at_death   = sub.victim_age,
            gender         = gender,
            community_ward = sub.community_ward,
            year_of_death  = sub.year_of_death,
            cause_of_death = sub.cause_of_death,
            biographical_note = sub.story,
            home_lat       = sub.home_lat,
            home_lng       = sub.home_lng,
            source         = f'Public submission #{sub.pk}',
            consent_status = ConsentStatus.CONSENTED if sub.submitter_consents else ConsentStatus.PENDING,
            added_by       = request.user,
        )
        sub.victim      = victim
        sub.status      = SubmissionStatus.APPROVED
        sub.reviewed_by = request.user
        sub.reviewed_at = timezone.now()
        sub.save()
        created += 1

    msg = f'{created} victim record(s) created.'
    if skipped:
        msg += f' {skipped} skipped (already linked).'
    modeladmin.message_user(request, msg, messages.SUCCESS)


# ── ModelAdmin ───────────────────────────────────────────────────────────────

@admin.register(PublicSubmission)
class PublicSubmissionAdmin(admin.ModelAdmin):
    list_display   = ['victim_name_col', 'community_ward', 'year_of_death',
                      'submitter_name', 'status_badge', 'created_at']
    list_filter    = ['status', 'victim_gender', 'year_of_death']
    search_fields  = ['victim_name', 'community_ward', 'submitter_name', 'submitter_contact']
    readonly_fields = ['ip_address', 'created_at', 'updated_at', 'victim']
    actions        = [approve_and_create, mark_under_review, mark_needs_info, reject_submissions]
    date_hierarchy  = 'created_at'
    list_per_page   = 30

    fieldsets = [
        ('Victim Information', {
            'fields': [
                'victim_name', ('victim_age', 'victim_gender'),
                'community_ward', 'year_of_death',
                'cause_of_death', 'story',
                ('home_lat', 'home_lng'),
            ],
        }),
        ('Submitter (never published)', {
            'fields': [
                'submitter_name', 'submitter_relationship',
                'submitter_contact', 'submitter_consents',
            ],
            'description': 'This section is confidential and will never appear on the public site.',
        }),
        ('Review', {
            'fields': ['status', 'reviewed_by', 'reviewed_at', 'review_notes', 'victim'],
        }),
        ('Meta', {
            'fields': ['ip_address', 'created_at', 'updated_at'],
            'classes': ['collapse'],
        }),
    ]

    def victim_name_col(self, obj):
        name = obj.victim_name or 'Name unknown'
        return format_html('<strong>{}</strong>', name)
    victim_name_col.short_description = 'Victim name'

    def status_badge(self, obj):
        cfg = {
            'SUBMITTED':    ('#1d4ed8', '#dbeafe', 'New'),
            'UNDER_REVIEW': ('#92400e', '#fef3c7', 'In Review'),
            'NEEDS_INFO':   ('#5b21b6', '#ede9fe', 'Needs Info'),
            'APPROVED':     ('#065f46', '#d1fae5', 'Approved'),
            'REJECTED':     ('#7f1d1d', '#fee2e2', 'Rejected'),
        }
        fg, bg, label = cfg.get(obj.status, ('#374151', '#f1f5f9', obj.status))
        return format_html(
            '<span style="background:{};color:{};padding:2px 9px;border-radius:12px;'
            'font-size:11px;font-weight:700">{}</span>',
            bg, fg, label,
        )
    status_badge.short_description = 'Status'
