from django.db import models
from django.contrib.auth.models import User


class SubmissionStatus(models.TextChoices):
    SUBMITTED    = 'SUBMITTED',    'Submitted'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
    NEEDS_INFO   = 'NEEDS_INFO',   'More Info Needed'
    APPROVED     = 'APPROVED',     'Approved'
    REJECTED     = 'REJECTED',     'Rejected'


class PublicSubmission(models.Model):
    # ── About the victim ──────────────────────────────────────────
    victim_name     = models.CharField(max_length=255, blank=True,
                        help_text='Leave blank if the name is unknown or withheld')
    victim_age      = models.PositiveSmallIntegerField(null=True, blank=True)
    victim_gender   = models.CharField(max_length=2, blank=True,
                        choices=[('M', 'Male'), ('F', 'Female'), ('NR', 'Not recorded')])
    community_ward  = models.CharField(max_length=255)
    year_of_death   = models.PositiveSmallIntegerField(null=True, blank=True)
    cause_of_death  = models.TextField(blank=True)
    story           = models.TextField(help_text='What you know about this person')

    # Optional location
    home_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    home_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # ── About the submitter (never published) ─────────────────────
    submitter_name         = models.CharField(max_length=255, blank=True)
    submitter_relationship = models.CharField(max_length=255, blank=True,
                               help_text='e.g. Family member, Neighbour, Community leader')
    submitter_contact      = models.CharField(max_length=255, blank=True,
                               help_text='Phone or email — only used for follow-up, never published')
    submitter_consents     = models.BooleanField(default=False,
                               help_text='Submitter confirms they have authority to share this information')

    # ── Verification ──────────────────────────────────────────────
    status       = models.CharField(max_length=15, choices=SubmissionStatus.choices,
                     default=SubmissionStatus.SUBMITTED)
    reviewed_by  = models.ForeignKey(User, null=True, blank=True,
                     on_delete=models.SET_NULL, related_name='reviewed_submissions')
    reviewed_at  = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    # Created Victim record (set on approval)
    victim = models.OneToOneField('victims.Victim', null=True, blank=True,
               on_delete=models.SET_NULL, related_name='submission')

    # ── Meta ──────────────────────────────────────────────────────
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        name = self.victim_name or 'Name unknown'
        return f'{name} — {self.community_ward} ({self.status})'
