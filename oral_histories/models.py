from django.db import models
from victims.models import Victim


class OralHistory(models.Model):
    victim = models.ForeignKey(Victim, on_delete=models.CASCADE, related_name='oral_histories')
    audio_file = models.FileField(upload_to='oral_histories/audio/', null=True, blank=True)
    transcript = models.TextField(blank=True)
    # Role only — no personal details of the interviewee
    interviewee_role = models.CharField(
        max_length=255,
        blank=True,
        help_text='e.g. Sister of victim, Community elder',
    )
    date_recorded = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_recorded']
        verbose_name_plural = 'Oral histories'

    def __str__(self):
        return f'Oral history for {self.victim} ({self.date_recorded or "undated"})'
