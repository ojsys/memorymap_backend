from django.db import models
from django.contrib.auth.models import User


class BulkImport(models.Model):
    STATUS = [
        ('PENDING',  'Pending Review'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    file              = models.FileField(upload_to='imports/')
    original_filename = models.CharField(max_length=255)
    uploaded_by       = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bulk_uploads')
    status            = models.CharField(max_length=10, choices=STATUS, default='PENDING')

    # Set by superadmin on review
    reviewed_by  = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='bulk_reviews')
    reviewed_at  = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)

    total_rows = models.PositiveIntegerField(default=0)
    valid_rows = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.original_filename} ({self.status})'


class BulkImportRow(models.Model):
    batch            = models.ForeignKey(BulkImport, on_delete=models.CASCADE, related_name='rows')
    row_number       = models.PositiveIntegerField()
    raw_data         = models.JSONField()
    is_valid         = models.BooleanField(default=True)
    validation_errors = models.JSONField(default=dict)
    # Populated after approval
    victim           = models.OneToOneField(
        'victims.Victim', null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ['row_number']
