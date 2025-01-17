from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate
from core.models import User
from user.views import UserModelViewSet

class UserMeTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(email='test@example.com', name='Test User')

    def test_get_me_valid_token(self):
        request = self.factory.get('/user/me')
        force_authenticate(request, user=self.user)
        view = UserModelViewSet.as_view({'get': 'me'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['email'], self.user.email)
    
    def test_me_no_token(self):
        request = self.factory.get('/user/me')
        force_authenticate(request, user=None)
        view = UserModelViewSet.as_view({'get': 'me'})
        response = view(request)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['error'], 'Not authenticated')
