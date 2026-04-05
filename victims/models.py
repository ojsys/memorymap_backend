from django.db import models
from django.contrib.auth.models import User


class ConsentStatus(models.TextChoices):
    CONSENTED = 'CONSENTED', 'Consented'
    ANONYMOUS = 'ANONYMOUS', 'Anonymous'
    PENDING = 'PENDING', 'Pending'


class Gender(models.TextChoices):
    MALE = 'M', 'Male'
    FEMALE = 'F', 'Female'
    NOT_RECORDED = 'NR', 'Not Recorded'


class Victim(models.Model):
    # Identity
    full_name = models.CharField(max_length=255)
    age_at_death = models.PositiveSmallIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=2, choices=Gender.choices, default=Gender.NOT_RECORDED)
    community_ward = models.CharField(max_length=255)

    # Death details
    date_of_death = models.DateField(null=True, blank=True)
    year_of_death = models.PositiveSmallIntegerField(null=True, blank=True)
    cause_of_death = models.TextField(blank=True)

    # Biography
    biographical_note = models.TextField(blank=True)

    # Locations (lat/lng pairs — no PostGIS required)
    home_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    home_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    incident_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    incident_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    burial_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    burial_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Source & consent
    source = models.TextField(help_text='e.g. Church register, NGO report, family interview')
    consent_status = models.CharField(
        max_length=10,
        choices=ConsentStatus.choices,
        default=ConsentStatus.PENDING,
    )
    consent_date = models.DateField(null=True, blank=True)
    consent_notes = models.TextField(blank=True)

    # Audit
    added_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='victims_added')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year_of_death', 'full_name']

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        if self.consent_status == ConsentStatus.ANONYMOUS:
            return 'Name Withheld'
        return self.full_name

    @property
    def effective_year(self):
        if self.date_of_death:
            return self.date_of_death.year
        return self.year_of_death
