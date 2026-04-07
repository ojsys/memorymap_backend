"""
Management command: seed_data
Populates the database with ~1890 plausible dummy victim records for Jos North,
Plateau State, Nigeria. All data is fictional and for development purposes only.
"""
import random
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from victims.models import Victim, ConsentStatus, Gender

# ── Names drawn from Berom, Hausa/Fulani, Igbo, and other
#    communities present in Plateau State ─────────────────

BEROM_FIRST = [
    'Danladi', 'Dalyop', 'Dung', 'Pam', 'Bot', 'Gyang', 'Rwang', 'Nde',
    'Bulus', 'Daspan', 'Fwangmun', 'Nanle', 'Bitrus', 'Yakubu', 'Gambo',
    'Luka', 'Sule', 'Davou', 'Choji', 'Tongkat', 'Gwom', 'Ayuba', 'Mwadkwon',
    'Damshak', 'Danboyi', 'Danasabe', 'Danfulani', 'Danmusa', 'Danlome',
]

HAUSA_FULANI_FIRST = [
    'Musa', 'Abubakar', 'Ibrahim', 'Garba', 'Bello', 'Usman', 'Aminu',
    'Lawal', 'Sani', 'Haruna', 'Yusuf', 'Aliyu', 'Isah', 'Muhammed',
    'Abdullahi', 'Auwal', 'Hamisu', 'Zubairu', 'Bashir', 'Kabiru',
    'Sadiya', 'Fatima', 'Hauwa', 'Aisha', 'Zainab', 'Maryam',
]

IGBO_FIRST = [
    'Emeka', 'Chukwuemeka', 'Ngozi', 'Chioma', 'Obiora', 'Uchenna',
    'Ikenna', 'Amaka', 'Chidi', 'Nnamdi',
]

YORUBA_FIRST = [
    'Taiwo', 'Kehinde', 'Adewale', 'Funmi', 'Tobi', 'Segun',
]

FEMALE_FIRST = [
    'Rebecca', 'Mary', 'Esther', 'Rifkatu', 'Jummai', 'Ramatu',
    'Patience', 'Blessing', 'Grace', 'Comfort', 'Saratu', 'Talatu',
    'Sadiya', 'Fatima', 'Hauwa', 'Aisha', 'Zainab', 'Maryam',
    'Ngozi', 'Chioma', 'Amaka', 'Funmi',
]

ALL_FIRST_MALE = BEROM_FIRST + HAUSA_FULANI_FIRST + IGBO_FIRST + YORUBA_FIRST + [
    'Sunday', 'Monday', 'Peter', 'John', 'James', 'Daniel', 'Joseph',
    'Emmanuel', 'Samuel', 'David', 'Simon', 'Philip', 'Mark', 'Luke',
    'Andrew', 'Matthew', 'Stephen', 'Timothy', 'Nathan', 'Solomon',
]

SURNAMES = [
    'Danladi', 'Gyang', 'Pam', 'Bot', 'Rwang', 'Dalyop', 'Bulus', 'Nde',
    'Yakubu', 'Musa', 'Ibrahim', 'Garba', 'Bello', 'Usman', 'Lawal',
    'Sani', 'Haruna', 'Yusuf', 'Aliyu', 'Abdullahi', 'Auwal', 'Hamisu',
    'Tanko', 'Jonah', 'Gomwalk', 'Lar', 'Fom', 'Nyam', 'Lot', 'Fwangmun',
    'Dung', 'Choji', 'Davou', 'Gwom', 'Ayuba', 'Luka', 'Gambo', 'Tongkat',
    'Jatau', 'Bitrus', 'Daspan', 'Nanle', 'Panshak', 'Zang', 'Danlome',
    'Emeka', 'Nnamdi', 'Uchenna', 'Obiora', 'Taiwo', 'Adewale',
    'Chukwu', 'Okafor', 'Nwosu', 'Eze', 'Obi',
]

# ── Communities in Jos North ─────────────────────────────

COMMUNITIES = [
    'Rikkos', 'Yan Gwoi', 'Dogon Karfe', 'Nasarawa Gwom', 'Angwan Rogo',
    'Tudun Wada', 'Gangare', 'Bauchi Road', 'Anglo Jos', 'Nassarawa',
    'Ali Kazaure', 'Maza Maza', 'Terminus', 'Congo Russia', 'Sarkin Arab',
    'Angwan Soya', 'Gwong', 'Katako', 'Dutse Uku', 'Rukuba Road',
    'Apata', 'Bukuru', 'Dadin Kowa', 'Farin Gada', 'Gada Biyu',
    'Jenta', 'Naraguta', 'Tafawa Balewa Road', 'Zaria Road', 'Rayfield',
    'Tudun Wada South', 'Angwan Rukuba', 'Kwariari', 'Laranto', 'Tina Junction',
]

# ── Conflict years (weighted toward peak periods) ────────
#    2001 Jos crisis, 2004, 2008, 2010 are historically violent
YEAR_WEIGHTS = {
    2001: 280, 2002: 35, 2003: 28, 2004: 95, 2005: 30, 2006: 25,
    2007: 22, 2008: 180, 2009: 45, 2010: 210, 2011: 65, 2012: 55,
    2013: 48, 2014: 90, 2015: 72, 2016: 58, 2017: 50, 2018: 45,
    2019: 40, 2020: 35, 2021: 38, 2022: 42, 2023: 35, 2024: 30,
}

CAUSES = [
    'Shot during violence', 'Killed during riots', 'Stabbed during attack',
    'Killed in crossfire', 'Burned in house fire during violence',
    'Machete attack', 'Killed during reprisal attack', 'Died of injuries sustained in attack',
    'Unknown cause during conflict', 'Killed at checkpoint',
]

BIO_TEMPLATES = [
    '{name} was a {occupation} in {community}. {pronoun} was {age} years old at the time of death and is survived by {family}.',
    '{name} lived and worked in {community} as a {occupation}. Known to {pronoun_lower} neighbours as a {trait} person.',
    'A resident of {community}, {name} was known for {known_for}. {pronoun} died during the {year} violence.',
    '{name} was {age} years old and worked as a {occupation}. {pronoun} had lived in {community} all {pronoun_lower} life.',
    '{name}, {age}, was a {occupation} in {community}. {pronoun} is remembered by family and neighbours for {known_for}.',
    '',  # Some records have no bio note
    '',
    '',
]

OCCUPATIONS = [
    'farmer', 'trader', 'teacher', 'student', 'civil servant', 'artisan',
    'mechanic', 'carpenter', 'tailor', 'pastor', 'imam', 'nurse',
    'market seller', 'bricklayer', 'driver', 'butcher', 'shopkeeper',
]

FAMILY = [
    'a wife and three children', 'a husband and two children', 'two young children',
    'elderly parents and siblings', 'a spouse and four children', 'no known surviving relatives',
    'a widow and five children', 'parents and a sibling', 'a young family',
    'a wife and newborn', 'an extended family',
]

KNOWN_FOR = [
    'generosity and community spirit', 'hard work and dedication to family',
    'kindness to neighbours', 'active participation in the local church',
    'his role in the community mosque', 'her skill as a trader',
    'his teaching at the local school', 'her warmth and hospitality',
]

TRAITS = ['kind', 'hardworking', 'generous', 'quiet', 'devoted', 'respected']

SOURCES = [
    'Family interview, {year}', 'Church register, St. Patrick\'s Jos',
    'Community register compiled by Stafanos Foundation',
    'NGO report, Search for Common Ground, {year}',
    'Survivor testimony recorded by project team',
    'Human Rights Watch report, {year}', 'Community elder testimony',
    'NEMA situational report', 'Jos North LGA records',
    'Christian Association of Nigeria register', 'Jama\'atu Nasril Islam records',
]

# ── Bounding box for Jos North (lat: 9.85–9.98, lng: 8.83–8.97) ─

JOS_LAT = (9.850, 9.980)
JOS_LNG = (8.830, 8.970)


def rand_coord():
    return (
        round(random.uniform(*JOS_LAT), 6),
        round(random.uniform(*JOS_LNG), 6),
    )


def build_name(gender):
    if gender == Gender.FEMALE:
        first = random.choice(FEMALE_FIRST)
    else:
        first = random.choice(ALL_FIRST_MALE)
    surname = random.choice(SURNAMES)
    return f'{first} {surname}'


def build_bio(name, gender, age, community, year):
    template = random.choice(BIO_TEMPLATES)
    if not template:
        return ''
    pronoun = 'She' if gender == Gender.FEMALE else 'He'
    return template.format(
        name=name,
        occupation=random.choice(OCCUPATIONS),
        community=community,
        pronoun=pronoun,
        pronoun_lower=pronoun.lower(),
        age=age or 'unknown age',
        family=random.choice(FAMILY),
        trait=random.choice(TRAITS),
        known_for=random.choice(KNOWN_FOR),
        year=year,
    )


def build_source(year):
    template = random.choice(SOURCES)
    return template.format(year=year)


def weighted_year():
    years = list(YEAR_WEIGHTS.keys())
    weights = list(YEAR_WEIGHTS.values())
    return random.choices(years, weights=weights, k=1)[0]


class Command(BaseCommand):
    help = 'Seed the database with ~1890 dummy victim records for development'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=1890)
        parser.add_argument('--clear', action='store_true', help='Delete existing records first')

    def handle(self, *args, **options):
        count = options['count']

        if options['clear']:
            deleted, _ = Victim.objects.all().delete()
            self.stdout.write(f'Cleared {deleted} existing records.')

        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            self.stderr.write('No superuser found. Run: python manage.py createsuperuser')
            return

        consent_pool = (
            [ConsentStatus.CONSENTED] * 78 +
            [ConsentStatus.ANONYMOUS] * 12 +
            [ConsentStatus.PENDING] * 10
        )

        created = 0
        batch = []

        for _ in range(count):
            gender = random.choices(
                [Gender.MALE, Gender.FEMALE, Gender.NOT_RECORDED],
                weights=[62, 33, 5],
            )[0]

            name = build_name(gender)
            year = weighted_year()
            age = random.choices(
                [None] + list(range(5, 80)),
                weights=[10] + [1] * 75,
            )[0]
            community = random.choice(COMMUNITIES)
            consent = random.choice(consent_pool)

            # Randomise which location types are present
            has_home = random.random() < 0.70
            has_incident = random.random() < 0.55
            has_burial = random.random() < 0.40

            home_lat = home_lng = None
            incident_lat = incident_lng = None
            burial_lat = burial_lng = None

            if has_home:
                home_lat, home_lng = rand_coord()
            if has_incident:
                incident_lat, incident_lng = rand_coord()
            if has_burial:
                burial_lat, burial_lng = rand_coord()

            batch.append(Victim(
                full_name=name,
                age_at_death=age,
                gender=gender,
                community_ward=community,
                year_of_death=year,
                cause_of_death=random.choices(
                    CAUSES + [''],
                    weights=[3] * len(CAUSES) + [8],
                )[0],
                biographical_note=build_bio(name, gender, age, community, year),
                home_lat=home_lat,
                home_lng=home_lng,
                incident_lat=incident_lat,
                incident_lng=incident_lng,
                burial_lat=burial_lat,
                burial_lng=burial_lng,
                source=build_source(year),
                consent_status=consent,
                added_by=admin,
            ))

            created += 1
            if len(batch) >= 200:
                Victim.objects.bulk_create(batch)
                batch = []
                self.stdout.write(f'  {created}/{count} records written…')

        if batch:
            Victim.objects.bulk_create(batch)

        self.stdout.write(self.style.SUCCESS(
            f'\nDone. {created} victim records created.'
        ))
