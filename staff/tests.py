from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from oral_histories.models import OralHistory
from victims.models import Victim


class StaffUsersTests(APITestCase):
    def setUp(self):
        self.admin  = User.objects.create_superuser('admin', 'a@x.org', 'Adm1n-pass-xyz')
        self.editor = User.objects.create_user('editor', password='Ed1tor-pass-xyz', is_staff=True)

    def test_editor_cannot_manage_staff(self):
        self.client.force_authenticate(self.editor)
        self.assertEqual(self.client.get('/api/staff/users/').status_code, 403)

    def test_admin_creates_verifier(self):
        self.client.force_authenticate(self.admin)
        r = self.client.post('/api/staff/users/', {
            'username': 'grace', 'first_name': 'Grace', 'role': 'verifier',
            'password': 'Str0ng-pass-xyz',
        })
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(r.data['role'], 'verifier')
        self.assertNotIn('password', r.data)
        u = User.objects.get(username='grace')
        self.assertTrue(u.is_staff)
        self.assertFalse(u.is_superuser)
        self.assertTrue(u.groups.filter(name='CVT').exists())
        self.assertTrue(u.check_password('Str0ng-pass-xyz'))

    def test_weak_password_rejected(self):
        self.client.force_authenticate(self.admin)
        r = self.client.post('/api/staff/users/', {'username': 'x', 'role': 'editor', 'password': '123'})
        self.assertEqual(r.status_code, 400)
        self.assertIn('password', r.data)

    def test_role_change_and_deactivate(self):
        self.client.force_authenticate(self.admin)
        r = self.client.patch(f'/api/staff/users/{self.editor.id}/', {'role': 'administrator', 'is_active': False}, format='json')
        self.assertEqual(r.status_code, 200, r.data)
        self.editor.refresh_from_db()
        self.assertTrue(self.editor.is_superuser)
        self.assertFalse(self.editor.is_active)

    def test_admin_cannot_lock_self_out(self):
        self.client.force_authenticate(self.admin)
        url = f'/api/staff/users/{self.admin.id}/'
        self.assertEqual(self.client.patch(url, {'is_active': False}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(url, {'role': 'editor'}, format='json').status_code, 400)

    def test_no_delete(self):
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.delete(f'/api/staff/users/{self.editor.id}/').status_code, 405)


class ProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('editor', password='Ed1tor-pass-xyz', is_staff=True)
        self.client.force_authenticate(self.user)

    def test_me_and_update_profile(self):
        self.assertEqual(self.client.get('/api/me/').data['role'], 'editor')
        r = self.client.patch('/api/me/', {'first_name': 'Oscar', 'is_superuser': True}, format='json')
        self.assertEqual(r.data['first_name'], 'Oscar')
        self.assertFalse(r.data['is_superuser'])

    def test_change_password(self):
        r = self.client.post('/api/me/password/', {'current_password': 'wrong', 'new_password': 'N3w-pass-xyz-1'})
        self.assertEqual(r.status_code, 400)
        r = self.client.post('/api/me/password/', {'current_password': 'Ed1tor-pass-xyz', 'new_password': 'N3w-pass-xyz-1'})
        self.assertEqual(r.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('N3w-pass-xyz-1'))


class OralHistoryConsentTests(APITestCase):
    def setUp(self):
        u = User.objects.create_user('editor', is_staff=True)
        kw = dict(community_ward='Rikkos', source='test', added_by=u)
        self.public  = Victim.objects.create(full_name='A', consent_status='CONSENTED', **kw)
        self.pending = Victim.objects.create(full_name='B', consent_status='PENDING', **kw)
        OralHistory.objects.create(victim=self.public, transcript='ok')
        OralHistory.objects.create(victim=self.pending, transcript='hidden')
        self.staff = u

    def test_public_hides_pending(self):
        r = self.client.get('/api/oral-histories/')
        self.assertEqual([h['victim'] for h in r.data['results']], [self.public.id])

    def test_victim_filter(self):
        self.client.force_authenticate(self.staff)
        r = self.client.get(f'/api/oral-histories/?victim={self.pending.id}')
        self.assertEqual(len(r.data['results']), 1)
        self.assertEqual(r.data['results'][0]['victim_name'], 'B')
