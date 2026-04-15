from django.contrib import admin
from django.utils.html import format_html
from .models import CommunityInitiative


@admin.register(CommunityInitiative)
class CommunityInitiativeAdmin(admin.ModelAdmin):
    list_display   = ['name', 'organising_body', 'date', 'location_name', 'has_url', 'has_coords']
    list_filter    = ['date']
    search_fields  = ['name', 'organising_body', 'description', 'location_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy  = 'date'
    list_per_page   = 25

    fieldsets = [
        ('Initiative Details', {
            'fields': ['name', 'organising_body', 'description'],
        }),
        ('When & Where', {
            'fields': ['date', 'location_name', ('location_lat', 'location_lng')],
        }),
        ('External Link', {
            'fields': ['url'],
        }),
        ('Record Info', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse'],
        }),
    ]

    def has_url(self, obj):
        if obj.url:
            return format_html(
                '<a href="{}" target="_blank" style="color:#4b6bfb;font-weight:600">Link ↗</a>',
                obj.url,
            )
        return format_html('<span style="color:#e2e8f0">—</span>')
    has_url.short_description = 'URL'

    def has_coords(self, obj):
        if obj.location_lat and obj.location_lng:
            return format_html('<span style="color:#10b981;font-weight:700">✓</span>')
        return format_html('<span style="color:#e2e8f0">—</span>')
    has_coords.short_description = 'Coords'
