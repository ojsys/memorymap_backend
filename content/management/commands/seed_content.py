"""
Populate SiteContent with the default copy for all editable sections.
Safe to re-run — uses get_or_create so it never overwrites edited values.

Usage:
    python manage.py seed_content
"""
from django.core.management.base import BaseCommand
from content.models import SiteContent

DEFAULTS = [
    # ── Site-wide ─────────────────────────────────────────────────────────
    dict(section='site', key='site_name',    label='Site name',        value='Mapping Memory'),
    dict(section='site', key='site_tagline', label='Site tagline',     value='Nigeria'),
    dict(section='site', key='site_nav_cta', label='Navbar CTA button',value='Submit a record'),

    # ── Hero section ──────────────────────────────────────────────────────
    dict(section='hero', key='hero_badge',    label='Phase badge text',
         value='JOS NORTH PILOT — PHASE 1'),
    dict(section='hero', key='hero_headline', label='Main headline',
         value='Remembering the names behind the numbers'),
    dict(section='hero', key='hero_headline_highlight', label='Headline highlighted word(s)',
         value='names behind'),
    dict(section='hero', key='hero_subtitle', label='Hero subtitle paragraph',
         value='A memorial register and digital map preserving the identities, stories, and places of individuals killed in communal and ethno-religious conflicts across Nigeria.'),
    dict(section='hero', key='hero_quote',    label='Inline hero quote',
         value='"If we cannot stop the killings, we can stop the erasure."'),
    dict(section='hero', key='hero_cta_map',      label='Primary CTA — map button',      value='Explore the map'),
    dict(section='hero', key='hero_cta_register', label='Secondary CTA — register button', value='Browse the register'),

    # ── Stats bar ─────────────────────────────────────────────────────────
    dict(section='stats', key='stats_communities_value', label='Communities piloted (number)',value='1'),
    dict(section='stats', key='stats_communities_label', label='Communities label',          value='COMMUNITY\nPILOTED'),
    dict(section='stats', key='stats_years_value',       label='Years documented (value)',   value='2001–2024'),
    dict(section='stats', key='stats_years_label',       label='Years documented label',     value='YEARS\nDOCUMENTED'),
    dict(section='stats', key='stats_names_label',       label='Names recorded label',       value='NAMES\nRECORDED'),
    dict(section='stats', key='stats_histories_label',   label='Oral histories label',       value='ORAL\nHISTORIES'),

    # ── Features section ──────────────────────────────────────────────────
    dict(section='features', key='features_section_label',   label='Section eyebrow label', value='PLATFORM FEATURES'),
    dict(section='features', key='features_heading',         label='Section heading',        value='Built for memory. Designed for dignity.'),
    dict(section='features', key='features_subheading',      label='Section subheading',     value='Every feature is shaped by the ethical responsibility of working with names of the dead and stories of the living.'),

    dict(section='features', key='feature_1_title',       label='Feature 1 — title',       value='Interactive Memorial Map'),
    dict(section='features', key='feature_1_description', label='Feature 1 — description', value='Colour-coded markers plot last known homes, incident sites, and burial grounds across documented communities.'),
    dict(section='features', key='feature_2_title',       label='Feature 2 — title',       value='Searchable Register'),
    dict(section='features', key='feature_2_description', label='Feature 2 — description', value='Browse and search victim records by name, gender, year, and community ward. Every name preserved with dignity.'),
    dict(section='features', key='feature_3_title',       label='Feature 3 — title',       value='Oral History Archive'),
    dict(section='features', key='feature_3_description', label='Feature 3 — description', value='Audio recordings and written testimonies from family members and witnesses, linked to individual profiles.'),
    dict(section='features', key='feature_4_title',       label='Feature 4 — title',       value='Community Initiatives'),
    dict(section='features', key='feature_4_description', label='Feature 4 — description', value='A curated record of local peacebuilding and remembrance activities, organised by communities across the documented regions.'),

    # ── Footer ────────────────────────────────────────────────────────────
    dict(section='footer', key='footer_quote',       label='Footer blockquote',       value='If we cannot stop the killings, we can at least stop the erasure.'),
    dict(section='footer', key='footer_attribution', label='Quote attribution',        value='Fwangmun Oscar Danladi — Mapping Memory, University of Iowa, 2025'),
    dict(section='footer', key='footer_copyright',   label='Copyright line',           value='© 2026 Mapping Memory · Plateau State, Nigeria · All records subject to community consent'),
    dict(section='footer', key='footer_link_privacy',    label='Footer link — Privacy',       value='Privacy'),
    dict(section='footer', key='footer_link_ethics',     label='Footer link — Ethics policy', value='Ethics policy'),
    dict(section='footer', key='footer_link_data',       label='Footer link — Data request',  value='Data request'),
    dict(section='footer', key='footer_link_contact',    label='Footer link — Contact',        value='Contact'),

    # ── Initiatives page ──────────────────────────────────────────────────
    dict(section='pages', key='initiatives_heading',    label='Initiatives page — heading',    value='Community Initiatives'),
    dict(section='pages', key='initiatives_subheading', label='Initiatives page — subheading', value='Local remembrance and peacebuilding activities across documented communities.'),

    # ── Submit page ───────────────────────────────────────────────────────
    dict(section='pages', key='submit_heading',    label='Submit page — heading',    value='Submit a Record'),
    dict(section='pages', key='submit_subheading', label='Submit page — subheading', value='Help preserve the memory of someone lost to violence in your community. All submissions are reviewed by our Community Verification Team before publication.'),
    dict(section='pages', key='submit_privacy_notice', label='Submit page — privacy notice', value='Submitter information is never published and is only used for follow-up if the verification team needs clarification.'),

    # ── Register page ─────────────────────────────────────────────────────
    dict(section='pages', key='register_intro',           label='Register page — intro text',          value='A record of individuals killed during ethno-religious and communal conflicts. All records are published with the consent of families or community representatives.'),
    dict(section='pages', key='register_years_covered',   label='Register page — years covered value',  value='2001–2024'),
    dict(section='pages', key='register_pilot_location',  label='Register page — pilot community name', value='Phase 1'),
    dict(section='pages', key='register_pilot_label',     label='Register page — pilot card label',     value='CURRENT\nPHASE'),

    # ── Map page ──────────────────────────────────────────────────────────
    dict(section='pages', key='map_area_label', label='Map — current coverage area label', value='Phase 1 coverage'),

    # ── Admin ─────────────────────────────────────────────────────────────
    dict(section='admin', key='admin_subtitle',  label='Admin panel subtitle (dashboard + login)', value='Conflict Documentation Platform'),
]


class Command(BaseCommand):
    help = 'Seed default CMS content (safe to re-run — never overwrites edited values)'

    def handle(self, *args, **options):
        created_count = 0
        for data in DEFAULTS:
            _, created = SiteContent.objects.get_or_create(
                key=data['key'],
                defaults={
                    'label':   data['label'],
                    'section': data['section'],
                    'value':   data['value'],
                },
            )
            if created:
                created_count += 1
                self.stdout.write(f"  + {data['key']}")

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. {created_count} new entries created, '
            f'{len(DEFAULTS) - created_count} already existed (not overwritten).'
        ))
