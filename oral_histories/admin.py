from django.contrib import admin
from django.utils.html import format_html
from .models import OralHistory


@admin.register(OralHistory)
class OralHistoryAdmin(admin.ModelAdmin):
    list_display   = ['victim_link', 'interviewee_role', 'has_audio', 'has_transcript', 'date_recorded', 'created_at']
    list_filter    = ['date_recorded']
    search_fields  = ['victim__full_name', 'transcript', 'interviewee_role']
    readonly_fields = ['created_at']
    date_hierarchy  = 'created_at'
    list_per_page   = 25

    fieldsets = [
        ('Linked Victim', {
            'fields': ['victim'],
        }),
        ('Testimony', {
            'fields': ['interviewee_role', 'transcript', 'audio_file', 'date_recorded'],
        }),
        ('Record Info', {
            'fields': ['created_at'],
            'classes': ['collapse'],
        }),
    ]

    def victim_link(self, obj):
        return format_html(
            '<a href="/admin/victims/victim/{}/change/">{}</a>',
            obj.victim_id, obj.victim.display_name,
        )
    victim_link.short_description = 'Victim'

    def has_audio(self, obj):
        if obj.audio_file:
            return format_html('<span style="color:#10b981;font-weight:700">✓ Audio</span>')
        return format_html('<span style="color:#e2e8f0">—</span>')
    has_audio.short_description = 'Audio'

    def has_transcript(self, obj):
        if obj.transcript and obj.transcript.strip():
            words = len(obj.transcript.split())
            return format_html('<span style="color:#4b6bfb">{} words</span>', words)
        return format_html('<span style="color:#e2e8f0">—</span>')
    has_transcript.short_description = 'Transcript'
