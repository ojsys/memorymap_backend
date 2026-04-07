"""
Create CVT (Community Verification Team) group and seed example CVT users.

Usage:
    python manage.py seed_cvt
"""
from django.contrib.auth.models import User, Group
from django.core.management.base import BaseCommand


CVT_USERS = [
    {'username': 'cvt_amaka',   'first_name': 'Amaka',   'last_name': 'Okafor',  'password': 'cvt-pass-2024'},
    {'username': 'cvt_ibrahim', 'first_name': 'Ibrahim', 'last_name': 'Musa',    'password': 'cvt-pass-2024'},
    {'username': 'cvt_grace',   'first_name': 'Grace',   'last_name': 'Danladi', 'password': 'cvt-pass-2024'},
]


class Command(BaseCommand):
    help = 'Create CVT group and seed Community Verification Team users'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='CVT')
        if created:
            self.stdout.write(self.style.SUCCESS("Created group: CVT"))
        else:
            self.stdout.write("Group CVT already exists.")

        for data in CVT_USERS:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name':  data['last_name'],
                    'is_staff':   True,   # needs is_staff to access admin ViewSets
                },
            )
            if created:
                user.set_password(data['password'])
                user.save()
                self.stdout.write(self.style.SUCCESS(f"  Created CVT user: {user.username}"))
            else:
                self.stdout.write(f"  User already exists: {user.username}")

            user.groups.add(group)

        self.stdout.write(self.style.SUCCESS("\nDone. CVT group and users are ready."))
        self.stdout.write(
            "  Default password for new users: cvt-pass-2024\n"
            "  (Change passwords via /admin/ before production deployment)"
        )
