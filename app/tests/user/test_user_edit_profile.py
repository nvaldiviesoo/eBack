from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate, APIClient
from core.models import User, Product
from product.views import ProductViewSet
import json

class TestUserEditProfile(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(email='test@example.com', name='Test User', is_staff=False)
        self.apiclient = APIClient()
        self.apiclient.force_authenticate(user=self.user)
        self.url = '/api/v1/user/edit_profile/'
    
    def test_edit_profile_valid(self):
        data = json.dumps({
            'name': 'Test User edit'
        })
        
        request = self.apiclient.put(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Test User edit')
    
    def test_edit_profile_email(self):
        data = json.dumps({
            'email': 'testedit@example.com',
            'name': 'Test User edit'
        })

        request = self.apiclient.put(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 400)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'test@example.com')
    
    def test_edit_profile_password(self):
        data = json.dumps({
            'password': '12345',
            'name': 'Test User edit'
        })

        request = self.apiclient.put(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 400)
    
    def test_edit_profile_unauthorized_params(self):
        data = json.dumps({
            'is_superuser': True
        })

        request = self.apiclient.put(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 400)
    
    def test_edit_profile_unauthorized(self):
        self.apiclient.force_authenticate(user=None)
        data = json.dumps({
            'name': 'Test User edit'
        })

        request = self.apiclient.put(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 403)

