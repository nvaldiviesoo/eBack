from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate, APIClient
from core.models import User

class TestGetAllUsers(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.staff_user = User.objects.create(email='staff@example.com', name='Staff User', is_staff=True)
        self.user = User.objects.create(email='test@example.com', name='Test User', is_staff=False)
        self.user2 = User.objects.create(email='test2@example.com', name='Test User2', is_staff=False)
        self.user3 = User.objects.create(email='test3@example.com', name='Test User3', is_staff=False)
        self.apiclient = APIClient()
        self.url = '/api/v1/user/all/'
    
    def test_get_all_users_not_authenticated(self):
        self.apiclient.force_authenticate(user=None)
        request = self.apiclient.get(self.url)
        self.assertEqual(request.status_code, 401)
    
    def test_get_all_users_not_staff(self):
        self.apiclient.force_authenticate(user=self.user)
        request = self.apiclient.get(self.url)
        self.assertEqual(request.status_code, 403)
    
    def test_get_all_users_valid(self):
        self.apiclient.force_authenticate(user=self.staff_user)
        request = self.apiclient.get(self.url)
        self.assertEqual(request.status_code, 200)
        self.assertEqual(len(request.data['data']), 4)