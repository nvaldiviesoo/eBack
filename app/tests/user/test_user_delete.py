from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate, APIClient
from core.models import User, Product
from product.views import ProductViewSet
import json

class TestUserDelete(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.staff_user = User.objects.create(email='staff@example.com', name='Staff User', is_staff=True)
        self.user = User.objects.create(email='test@example.com', name='Test User', is_staff=False)
        self.apiclient = APIClient()
        self.apiclient.force_authenticate(user=self.staff_user)
        self.url = '/api/v1/user/delete/'
    
    def test_delete_user_not_authenticated(self):
        self.apiclient.force_authenticate(user=None)
        data = json.dumps({
            'id': str(self.user.id),
        })
        
        request = self.apiclient.delete(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 403)
    
    def test_delete_user_not_staff(self):
        self.apiclient.force_authenticate(user=self.user)
        data = json.dumps({
            'id': str(self.user.id),
        })
        
        request = self.apiclient.delete(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 403)
    
    def test_delete_user_valid(self):
        data = json.dumps({
            'id': str(self.user.id),
        })
        
        request = self.apiclient.delete(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 200)