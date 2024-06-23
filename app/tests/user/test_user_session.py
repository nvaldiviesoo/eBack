from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate, APIClient
from core.models import User, Product
from product.views import ProductViewSet
import json
import uuid

class TestUserSession(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(email='test@example.com', name='Test User', is_staff=False)
        self.apiclient = APIClient()
    
    def test_sign_up_user(self):
        data = json.dumps({
            'email': 'signup@test.com',
            'name': 'Test SignUP',
            'password': 'testpassword'
        })
        request = self.apiclient.post('/api/v1/user/sign_up/', data, content_type='application/json')
        self.assertEqual(request.status_code, 200)
    
    def test_sign_up_user_invalid_data(self):
        data = json.dumps({
            'email': 'signup2@test.com',
            'name': 'Test SignUP',
        })
        request = self.apiclient.post('/api/v1/user/sign_up/', data, content_type='application/json')
        self.assertEqual(request.status_code, 400)
    
    def test_forgot_password(self):
        data = json.dumps({
            'email': 'test@example.com',
        })
        request = self.apiclient.post('/api/v1/user/forgot_password/', data, content_type='application/json')
        self.assertEqual(request.status_code, 200)
    