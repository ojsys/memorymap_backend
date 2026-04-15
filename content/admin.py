from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import SiteContent

SECTION_ORDER = [
    'site', 'hero', 'stats', 'features', 'showcase', 'oral',
    'cta', 'initiatives_preview', 'about', 'pages', 'footer', 'admin',
]

SECTION_LABELS = {
    'site':                'Site-wide',
    'hero':                'Hero section',
    'stats':               'Stats bar',
    'features':            'Features section',
    'showcase':            'Victims showcase',
    'oral':                'Oral history spotlight',
    'cta':                 'CTA banner',
    'initiatives_preview': 'Initiatives preview',
    'about':               'About page',
    'pages':               'Other pages (Submit / Register / Map / Initiatives)',
    'footer':              'Footer',
    'admin':               'Admin panel',
}

# Keys whose values are long text — render as a taller textarea
LONG_VALUE_KEYS = {
    'hero_subtitle', 'hero_quote',
    'features_subheading',
    'feature_1_description', 'feature_2_description',
    'feature_3_description', 'feature_4_description',
    'showcase_subheading',
    'oral_spotlight_subheading',
    'cta_banner_body',
    'initiatives_preview_subheading',
    'about_mission_body', 'about_why_body', 'about_method_body',
    'about_contribute_body', 'about_contact_body',
    'submit_subheading', 'submit_privacy_notice',
    'register_intro',
    'footer_quote', 'footer_attribution', 'footer_copyright',
}


class SiteContentForm(forms.ModelForm):
    class Meta:
        model = SiteContent
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.key in LONG_VALUE_KEYS:
            self.fields['value'].widget = forms.Textarea(
                attrs={'rows': 4, 'style': 'width:100%;font-size:13px'}
            )
        else:
            self.fields['value'].widget = forms.TextInput(
                attrs={'style': 'width:100%;font-size:13px'}
            )


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    form           = SiteContentForm
    list_display   = ['label', 'key_col', 'section_badge', 'value_preview', 'updated_at']
    list_filter    = ['section']
    search_fields  = ['key', 'label', 'value', 'section']
    readonly_fields = ['key', 'updated_at']
    list_per_page   = 100
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

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Build an ordered section guide for the sidebar / top of page
        extra_context['section_guide'] = [
            (k, SECTION_LABELS.get(k, k))
            for k in SECTION_ORDER
        ]
        return super().changelist_view(request, extra_context=extra_context)

    def key_col(self, obj):
        return format_html(
            '<code style="background:#eef2ff;color:#4b6bfb;padding:1px 6px;'
            'border-radius:4px;font-size:11px">{}</code>',
            obj.key,
        )
    key_col.short_description = 'Key'

    def section_badge(self, obj):
        label = SECTION_LABELS.get(obj.section, obj.section)
        return format_html(
            '<span style="background:#f0f4ff;color:#0f1c5c;padding:2px 8px;'
            'border-radius:10px;font-size:11px;font-weight:600">{}</span>',
            label,
        )
    section_badge.short_description = 'Section'

    def value_preview(self, obj):
        text = obj.value or ''
        truncated = text[:100] + ('\u2026' if len(text) > 100 else '')
        return format_html('<span style="color:#64748b;font-size:12px">{}</span>', truncated)
    value_preview.short_description = 'Value'
