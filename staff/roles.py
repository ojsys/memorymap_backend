"""
WordPress-style roles for the staff admin panel, mapped onto Django's
built-in flags and groups so no extra tables are needed:

    administrator → is_superuser (manages staff, approves imports, deletes)
    editor        → is_staff     (adds and edits records and site content)
    verifier      → is_staff + CVT group (reviews community submissions)
"""
from django.contrib.auth.models import Group

ADMINISTRATOR = 'administrator'
EDITOR        = 'editor'
VERIFIER      = 'verifier'

ROLE_CHOICES = [
    (ADMINISTRATOR, 'Administrator'),
    (EDITOR,        'Editor'),
    (VERIFIER,      'Verifier (CVT)'),
]

CVT_GROUP = 'CVT'


def get_role(user):
    if user.is_superuser:
        return ADMINISTRATOR
    if user.groups.filter(name=CVT_GROUP).exists():
        return VERIFIER
    return EDITOR


def set_role(user, role):
    """Apply a role to a saved user."""
    cvt, _ = Group.objects.get_or_create(name=CVT_GROUP)
    user.is_staff     = True
    user.is_superuser = role == ADMINISTRATOR
    user.save(update_fields=['is_staff', 'is_superuser'])
    if role == VERIFIER:
        user.groups.add(cvt)
    else:
        user.groups.remove(cvt)
