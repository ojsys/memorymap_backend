from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.contrib import messages
from .models import BulkImport, BulkImportRow


# ── Admin actions ────────────────────────────────────────────────────────────

@admin.action(description='Approve selected imports')
def approve_imports(modeladmin, request, queryset):
    updated = queryset.filter(status='PENDING').update(
        status='APPROVED',
        reviewed_by=request.user,
        reviewed_at=timezone.now(),
    )
    modeladmin.message_user(request, f'{updated} import(s) approved.', messages.SUCCESS)


@admin.action(description='Reject selected imports')
def reject_imports(modeladmin, request, queryset):
    updated = queryset.filter(status='PENDING').update(
        status='REJECTED',
        reviewed_by=request.user,
        reviewed_at=timezone.now(),
    )
    modeladmin.message_user(request, f'{updated} import(s) rejected.', messages.WARNING)


# ── Inline ───────────────────────────────────────────────────────────────────

class BulkImportRowInline(admin.TabularInline):
    model           = BulkImportRow
    extra           = 0
    max_num         = 0
    can_delete      = False
    readonly_fields = ['row_number', 'validity_badge', 'raw_data_preview', 'validation_errors', 'victim']
    fields          = ['row_number', 'validity_badge', 'raw_data_preview', 'validation_errors', 'victim']
    verbose_name    = 'Row'
    verbose_name_plural = 'Rows (preview — first 50)'

    def get_queryset(self, request):
        return super().get_queryset(request)[:50]

    def validity_badge(self, obj):
        if obj.is_valid:
            return format_html('<span style="color:#10b981;font-weight:700">✓ Valid</span>')
        return format_html('<span style="color:#ef4444;font-weight:700">✗ Invalid</span>')
    validity_badge.short_description = 'Valid?'

    def raw_data_preview(self, obj):
        items = list(obj.raw_data.items())[:4]
        parts = [f'<span style="color:#64748b">{k}:</span> {v}' for k, v in items]
        if len(obj.raw_data) > 4:
            parts.append(f'<span style="color:#94a3b8">+{len(obj.raw_data)-4} more</span>')
        return format_html('<div style="font-size:11px;line-height:1.7">{}</div>',
                           format_html('<br>'.join(parts)))
    raw_data_preview.short_description = 'Data'


# ── ModelAdmin ───────────────────────────────────────────────────────────────

@admin.register(BulkImport)
class BulkImportAdmin(admin.ModelAdmin):
    inlines        = [BulkImportRowInline]
    list_display   = ['original_filename', 'uploaded_by', 'row_summary',
                      'status_badge', 'created_at']
    list_filter    = ['status']
    search_fields  = ['original_filename', 'uploaded_by__username']
    readonly_fields = ['uploaded_by', 'original_filename', 'total_rows', 'valid_rows',
                       'created_at', 'reviewed_by', 'reviewed_at']
    actions        = [approve_imports, reject_imports]
    date_hierarchy  = 'created_at'
    list_per_page   = 20

    fieldsets = [
        ('File', {
            'fields': ['file', 'original_filename', 'uploaded_by', 'created_at'],
        }),
        ('Validation Summary', {
            'fields': [('total_rows', 'valid_rows')],
        }),
        ('Review Decision', {
            'fields': ['status', 'reviewed_by', 'reviewed_at', 'review_notes'],
        }),
    ]

    def row_summary(self, obj):
        if obj.total_rows:
            pct = int(obj.valid_rows / obj.total_rows * 100)
            color = '#10b981' if pct >= 90 else '#f59e0b' if pct >= 60 else '#ef4444'
            return format_html(
                '<span style="color:{};font-weight:600">{}/{}</span>'
                '<span style="color:#94a3b8;font-size:11px"> ({}% valid)</span>',
                color, obj.valid_rows, obj.total_rows, pct,
            )
        return format_html('<span style="color:#94a3b8">—</span>')
    row_summary.short_description = 'Rows (valid/total)'

    def status_badge(self, obj):
        cfg = {
            'PENDING':  ('#92400e', '#fef3c7', 'Pending'),
            'APPROVED': ('#065f46', '#d1fae5', 'Approved'),
            'REJECTED': ('#7f1d1d', '#fee2e2', 'Rejected'),
        }
        fg, bg, label = cfg.get(obj.status, ('#374151', '#f1f5f9', obj.status))
        return format_html(
            '<span style="background:{};color:{};padding:2px 9px;border-radius:12px;'
            'font-size:11px;font-weight:700">{}</span>',
            bg, fg, label,
        )
    status_badge.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
