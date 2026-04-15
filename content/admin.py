from django.contrib import admin
from django.utils.html import format_html
from .models import SiteContent


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display   = ['label', 'key_col', 'section_badge', 'value_preview', 'updated_at']
    list_filter    = ['section']
    search_fields  = ['key', 'label', 'value', 'section']
    readonly_fields = ['key', 'updated_at']
    list_per_page   = 50
    ordering        = ['section', 'key']

    fieldsets = [
        ('Content', {
            'fields': ['label', 'key', 'section', 'value'],
        }),
        ('Meta', {
            'fields': ['updated_at'],
            'classes': ['collapse'],
        }),
    ]

    def key_col(self, obj):
        return format_html('<code style="background:#eef2ff;color:#4b6bfb;padding:1px 6px;border-radius:4px;font-size:11px">{}</code>', obj.key)
    key_col.short_description = 'Key'

    def section_badge(self, obj):
        return format_html(
            '<span style="background:#f0f4ff;color:#0f1c5c;padding:2px 8px;border-radius:10px;'
            'font-size:11px;font-weight:600">{}</span>',
            obj.section,
        )
    section_badge.short_description = 'Section'

    def value_preview(self, obj):
        text = obj.value or ''
        truncated = text[:80] + ('…' if len(text) > 80 else '')
        return format_html('<span style="color:#64748b;font-size:12px">{}</span>', truncated)
    value_preview.short_description = 'Value'
