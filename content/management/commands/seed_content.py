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
    dict(section='site', key='site_name',    label='Site name',         value='Middle Belt Memorial'),
    dict(section='site', key='site_tagline', label='Site tagline',      value='Nigeria'),
    dict(section='site', key='site_nav_cta', label='Navbar CTA button', value='Submit a record'),

    # ── Hero section ──────────────────────────────────────────────────────
    dict(section='hero', key='hero_badge',    label='Hero badge text',
         value='MIDDLE BELT, NIGERIA'),
    dict(section='hero', key='hero_headline', label='Main headline',
         value='Remembering the names behind the numbers'),
    dict(section='hero', key='hero_headline_highlight', label='Headline highlighted word(s)',
         value='names behind'),
    dict(section='hero', key='hero_subtitle', label='Hero subtitle paragraph',
         value='A memorial register and digital map preserving the identities, stories, and places of individuals killed in communal and ethno-religious conflicts across Nigeria.'),
    dict(section='hero', key='hero_quote',    label='Inline hero quote',
         value='\u201cIf we cannot stop the killings, we can stop the erasure.\u201d'),
    dict(section='hero', key='hero_cta_map',      label='Primary CTA \u2014 map button',       value='Explore the map'),
    dict(section='hero', key='hero_cta_register', label='Secondary CTA \u2014 register button', value='Browse the register'),

    # ── Stats bar ─────────────────────────────────────────────────────────
    dict(section='stats', key='stats_communities_value', label='States covered (number)',    value='1'),
    dict(section='stats', key='stats_communities_label', label='States covered label',       value='STATES\nCOVERED'),
    dict(section='stats', key='stats_years_value',       label='Years documented (value)',   value='2001\u20132024'),
    dict(section='stats', key='stats_years_label',       label='Years documented label',     value='YEARS\nDOCUMENTED'),
    dict(section='stats', key='stats_names_label',       label='Names recorded label',       value='NAMES\nRECORDED'),
    dict(section='stats', key='stats_histories_label',   label='Oral histories label',       value='ORAL\nHISTORIES'),

    # ── Features section ──────────────────────────────────────────────────
    dict(section='features', key='features_section_label', label='Section eyebrow label', value='PLATFORM FEATURES'),
    dict(section='features', key='features_heading',       label='Section heading',        value='Built for memory. Designed for dignity.'),
    dict(section='features', key='features_subheading',    label='Section subheading',
         value='Every feature is shaped by the ethical responsibility of working with names of the dead and stories of the living.'),

    dict(section='features', key='feature_1_title',       label='Feature 1 \u2014 title',       value='Interactive Memorial Map'),
    dict(section='features', key='feature_1_description', label='Feature 1 \u2014 description',
         value='Colour-coded markers plot last known homes, incident sites, and burial grounds across Middle Belt states.'),
    dict(section='features', key='feature_2_title',       label='Feature 2 \u2014 title',       value='Searchable Register'),
    dict(section='features', key='feature_2_description', label='Feature 2 \u2014 description',
         value='Browse and search victim records by name, gender, year, and community ward. Every name preserved with dignity.'),
    dict(section='features', key='feature_3_title',       label='Feature 3 \u2014 title',       value='Oral History Archive'),
    dict(section='features', key='feature_3_description', label='Feature 3 \u2014 description',
         value='Audio recordings and written testimonies from family members and witnesses, linked to individual profiles.'),
    dict(section='features', key='feature_4_title',       label='Feature 4 \u2014 title',       value='Community Initiatives'),
    dict(section='features', key='feature_4_description', label='Feature 4 \u2014 description',
         value='A curated record of local peacebuilding and remembrance activities, organised by communities across the documented regions.'),

    # ── Victims showcase (homepage) ───────────────────────────────────────
    dict(section='showcase', key='showcase_heading',    label='Showcase section \u2014 heading',
         value='From the memorial register'),
    dict(section='showcase', key='showcase_subheading', label='Showcase section \u2014 subheading',
         value='Recently documented individuals. Each record is published with the consent of families or community representatives.'),

    # ── Oral history spotlight (homepage) ─────────────────────────────────
    dict(section='oral', key='oral_spotlight_heading',    label='Oral spotlight \u2014 heading',
         value='A voice from the community'),
    dict(section='oral', key='oral_spotlight_subheading', label='Oral spotlight \u2014 subheading',
         value='Oral histories preserve not just names, but context \u2014 the relationships, the circumstances, and the grief of those left behind.'),

    # ── CTA banner (homepage) ─────────────────────────────────────────────
    dict(section='cta', key='cta_banner_heading', label='CTA banner \u2014 heading',
         value='Does your community have names to preserve?'),
    dict(section='cta', key='cta_banner_body',    label='CTA banner \u2014 body text',
         value='This memorial grows through community contribution. If you have information about a victim of communal violence in the Middle Belt region, you can submit a record for review.'),
    dict(section='cta', key='cta_banner_cta',     label='CTA banner \u2014 button label', value='Submit a record'),

    # ── Initiatives preview (homepage) ────────────────────────────────────
    dict(section='initiatives_preview', key='initiatives_preview_heading',    label='Initiatives preview \u2014 heading',
         value='Communities in action'),
    dict(section='initiatives_preview', key='initiatives_preview_subheading', label='Initiatives preview \u2014 subheading',
         value='Local peacebuilding and remembrance activities organised by communities across the Middle Belt region.'),

    # ── About page ────────────────────────────────────────────────────────
    dict(section='about', key='about_mission_heading',    label='About \u2014 mission heading',
         value='About the Middle Belt Memorial'),
    dict(section='about', key='about_mission_body',       label='About \u2014 mission body',
         value='The Middle Belt Memorial is a documentation project dedicated to preserving the names, stories, and histories of individuals killed during ethno-religious and communal conflicts across the Middle Belt region of Nigeria. We believe that every life lost deserves to be remembered \u2014 not as a statistic, but as a person with a name, a family, and a community.'),
    dict(section='about', key='about_why_heading',        label='About \u2014 why heading',
         value='Why this project exists'),
    dict(section='about', key='about_why_body',           label='About \u2014 why body',
         value='Decades of recurring violence across the Middle Belt states of Nigeria have left behind thousands of unnamed victims. Official records are incomplete, fragmented, or inaccessible. Families have mourned without public acknowledgement. This platform is built to close that gap \u2014 creating a permanent, searchable, and dignified record that communities, researchers, journalists, and policymakers can access and contribute to.'),
    dict(section='about', key='about_method_heading',     label='About \u2014 method heading',
         value='How records are collected'),
    dict(section='about', key='about_method_body',        label='About \u2014 method body',
         value='Records are gathered through community engagement \u2014 working directly with families, community leaders, and local organisations in affected areas. Each record is only published with the informed consent of a family member or designated community representative. Where consent for naming has not been given, individuals are recorded anonymously. No record is published without verification.'),
    dict(section='about', key='about_ethics_heading',     label='About \u2014 ethics heading',
         value='Our ethical commitments'),
    dict(section='about', key='about_contribute_heading', label='About \u2014 contribute heading',
         value='Contribute a record'),
    dict(section='about', key='about_contribute_body',    label='About \u2014 contribute body',
         value='If you have information about a victim of communal violence anywhere in the Middle Belt region \u2014 a family member, neighbour, or community member \u2014 you can submit a record for review. All submissions go through a consent and verification process before publication.'),
    dict(section='about', key='about_contact_heading',    label='About \u2014 contact heading',
         value='Contact'),
    dict(section='about', key='about_contact_body',       label='About \u2014 contact body',
         value='For enquiries about the project, research partnerships, or data requests, please reach out through the submission form or contact the project team directly.'),

    # ── Initiatives page ──────────────────────────────────────────────────
    dict(section='pages', key='initiatives_heading',    label='Initiatives page \u2014 heading',    value='Community Initiatives'),
    dict(section='pages', key='initiatives_subheading', label='Initiatives page \u2014 subheading',
         value='Local remembrance and peacebuilding activities across the Middle Belt region of Nigeria.'),

    # ── Submit page ───────────────────────────────────────────────────────
    dict(section='pages', key='submit_heading',       label='Submit page \u2014 heading',    value='Submit a Record'),
    dict(section='pages', key='submit_subheading',    label='Submit page \u2014 subheading',
         value='Help preserve the memory of someone lost to violence in your community. All submissions are reviewed by our Community Verification Team before publication.'),
    dict(section='pages', key='submit_privacy_notice', label='Submit page \u2014 privacy notice',
         value='Submitter information is never published and is only used for follow-up if the verification team needs clarification.'),

    # ── Register page ─────────────────────────────────────────────────────
    dict(section='pages', key='register_intro',         label='Register page \u2014 intro text',
         value='A record of individuals killed during ethno-religious and communal conflicts. All records are published with the consent of families or community representatives.'),
    dict(section='pages', key='register_years_covered', label='Register page \u2014 years covered value', value='2001\u20132024'),
    dict(section='pages', key='register_pilot_location', label='Register page \u2014 coverage region',    value='Middle Belt'),
    dict(section='pages', key='register_pilot_label',    label='Register page \u2014 coverage label',     value='COVERAGE\nREGION'),

    # ── Map page ──────────────────────────────────────────────────────────
    dict(section='pages', key='map_area_label', label='Map \u2014 coverage area label', value='Middle Belt, Nigeria'),

    # ── Footer ────────────────────────────────────────────────────────────
    dict(section='footer', key='footer_quote',
         label='Footer blockquote',
         value='If we cannot stop the killings, we can at least stop the erasure.'),
    dict(section='footer', key='footer_attribution',
         label='Quote attribution',
         value='Fwangmun Oscar Danladi \u2014 Mapping Memory, University of Iowa, 2025'),
    dict(section='footer', key='footer_copyright',
         label='Copyright line',
         value='\u00a9 2026 Middle Belt Memorial \u00b7 Nigeria \u00b7 All records subject to community consent'),
    dict(section='footer', key='footer_link_privacy',  label='Footer link \u2014 Privacy',       value='Privacy'),
    dict(section='footer', key='footer_link_ethics',   label='Footer link \u2014 Ethics policy', value='Ethics policy'),
    dict(section='footer', key='footer_link_data',     label='Footer link \u2014 Data request',  value='Data request'),
    dict(section='footer', key='footer_link_contact',  label='Footer link \u2014 Contact',       value='Contact'),

    # ── Admin ─────────────────────────────────────────────────────────────
    dict(section='admin', key='admin_subtitle',
         label='Admin panel subtitle (dashboard + login)',
         value='Conflict Documentation Platform'),
]


class Command(BaseCommand):
    help = 'Seed default CMS content (safe to re-run — never overwrites edited values)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite existing values with the defaults (use with care)',
        )

    def handle(self, *args, **options):
        overwrite = options['overwrite']
        created_count = 0
        updated_count = 0

        for data in DEFAULTS:
            obj, created = SiteContent.objects.get_or_create(
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
            elif overwrite:
                obj.label   = data['label']
                obj.section = data['section']
                obj.value   = data['value']
                obj.save()
                updated_count += 1
                self.stdout.write(f"  ~ {data['key']} (overwritten)")

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. {created_count} new entries created'
            + (f', {updated_count} overwritten' if updated_count else '')
            + f', {len(DEFAULTS) - created_count - updated_count} already existed (not touched).'
        ))
