from django.db import models


class SiteContent(models.Model):
    key        = models.SlugField(max_length=120, unique=True)
    label      = models.CharField(max_length=200, help_text='Human-readable name shown in the admin panel')
    section    = models.CharField(max_length=60,  help_text='Grouping label e.g. hero, features, footer')
    value      = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['section', 'key']

    def __str__(self):
        return f'[{self.section}] {self.label}'
