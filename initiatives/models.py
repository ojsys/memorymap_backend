from django.db import models


class CommunityInitiative(models.Model):
    name = models.CharField(max_length=255)
    organising_body = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(null=True, blank=True)
    location_name = models.CharField(max_length=255, blank=True)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.name
