from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate, APIClient
from core.models import User, Product
from product.views import ProductViewSet
import json
import uuid

class TestUserStaff(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.staff_user = User.objects.create(email='staff@example.com', name='Staff User', is_staff=True)
        self.no_staff_user = User.objects.create(email='nostaff@example.com', name='No Staff User', is_staff=False)
        self.user = User.objects.create(email='test@example.com', name='Test User', is_staff=False, balance=2000)
        self.apiclient = APIClient()
        self.apiclient.force_authenticate(user=self.staff_user)
        self.url = '/api/v1/user/edit_balance/'
    
    def test_edit_balance_not_authenticated(self):
        self.apiclient.force_authenticate(user=None)
        data = json.dumps({
            'id': str(self.user.id),	
            'balance': 100,
        })
        request = self.apiclient.patch(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 401)
    
    def test_edit_balance_not_staff(self):
        self.apiclient.force_authenticate(user=self.no_staff_user)
        data = json.dumps({
            'id': str(self.user.id),	
            'balance': 100,
        })
        request = self.apiclient.patch(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 403)
    
    def test_edit_balance_not_id(self):
        data = json.dumps({
            'balance': 100,
        })
        request = self.apiclient.patch(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 400)
    
    def test_edit_balance_not_balance(self):
        data = json.dumps({
            'id': str(self.user.id),	
        })
        request = self.apiclient.patch(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 400)
    
    def test_balance_not_number(self):
        data = json.dumps({
            'id': str(self.user.id),	
            'balance': '100k',
        })
        request = self.apiclient.patch(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 400)
    
    def test_edit_balance_negative(self):
        data = json.dumps({
            'id': str(self.user.id),	
            'balance': -100,
        })
        request = self.apiclient.patch(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 400)
    
    def test_edit_balance_valid(self):
        data = json.dumps({
            'id': str(self.user.id),	
            'balance': 100,
        })
        request = self.apiclient.patch(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, 2100)
    
    def test_edit_balance_not_found(self):
        data = json.dumps({
            'id': str(uuid.uuid4()),	
            'balance': 100,
        })
        request = self.apiclient.patch(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 404)