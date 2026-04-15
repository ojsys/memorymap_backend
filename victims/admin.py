from django.contrib import admin
from django.utils.html import format_html
from .models import Victim, ConsentStatus
from oral_histories.models import OralHistory


class OralHistoryInline(admin.StackedInline):
    model = OralHistory
    extra = 0
    fields = ['interviewee_role', 'transcript', 'audio_file', 'date_recorded']
    verbose_name = 'Oral history'
    verbose_name_plural = 'Oral histories'


@admin.register(Victim)
class VictimAdmin(admin.ModelAdmin):
    inlines        = [OralHistoryInline]
    list_per_page  = 30
    date_hierarchy = 'created_at'
    show_full_result_count = True

    list_display = [
        'display_name', 'community_ward', 'gender', 'effective_year',
        'consent_badge', 'oral_count', 'mapped_icon', 'created_at',
    ]
    list_filter  = ['consent_status', 'gender', 'year_of_death']
    search_fields = ['full_name', 'community_ward', 'biographical_note', 'source']
    readonly_fields = ['display_name', 'effective_year', 'added_by', 'created_at', 'updated_at']

    fieldsets = [
        ('Identity', {
            'fields': ['full_name', ('age_at_death', 'gender')],
        }),
        ('Death Details', {
            'fields': ['community_ward', ('date_of_death', 'year_of_death'), 'cause_of_death'],
        }),
        ('Biography', {
            'fields': ['biographical_note'],
            'classes': ['collapse'],
        }),
        ('Locations', {
            'fields': [
                ('home_lat', 'home_lng'),
                ('incident_lat', 'incident_lng'),
                ('burial_lat', 'burial_lng'),
            ],
            'classes': ['collapse'],
        }),
        ('Consent & Source', {
            'fields': ['consent_status', 'consent_date', 'consent_notes', 'source'],
        }),
        ('Record Info', {
            'fields': ['display_name', 'effective_year', 'added_by', 'created_at', 'updated_at'],
            'classes': ['collapse'],
        }),
    ]

    # ── Custom columns ──────────────────────────────────────────────────────

    def consent_badge(self, obj):
        cfg = {
            ConsentStatus.CONSENTED: ('#10b981', '#d1fae5', 'Consented'),
            ConsentStatus.ANONYMOUS: ('#64748b', '#f1f5f9', 'Anonymous'),
            ConsentStatus.PENDING:   ('#f59e0b', '#fef3c7', 'Pending'),
        }
        fg, bg, label = cfg.get(obj.consent_status, ('#94a3b8', '#f8fafc', obj.consent_status))
        return format_html(
            '<span style="background:{};color:{};padding:2px 9px;border-radius:12px;'
            'font-size:11px;font-weight:700">{}</span>',
            bg, fg, label,
        )
    consent_badge.short_description = 'Consent'

    def oral_count(self, obj):
        n = obj.oral_histories.count()
        if n:
            return format_html('<span style="color:#4b6bfb;font-weight:600">● {}</span>', n)
        return format_html('<span style="color:#cbd5e1">—</span>')
    oral_count.short_description = 'Oral'

    def mapped_icon(self, obj):
        if any([obj.home_lat, obj.incident_lat, obj.burial_lat]):
            return format_html('<span style="color:#10b981;font-weight:700">✓</span>')
        return format_html('<span style="color:#e2e8f0">—</span>')
    mapped_icon.short_description = 'Map'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)
