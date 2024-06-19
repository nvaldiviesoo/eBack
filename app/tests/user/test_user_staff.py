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
        self.user = User.objects.create(email='test@example.com', name='Test User', is_staff=False)
        self.apiclient = APIClient()
        self.apiclient.force_authenticate(user=self.staff_user)
        self.url = '/api/v1/user/staff/?id='
    
    def test_make_user_staff_not_authenticated(self):
        self.apiclient.force_authenticate(user=None)
        data = json.dumps({
            'is_staff': True,
        })
        request = self.apiclient.put(self.url + str(self.user.id), data, content_type='application/json')
        self.assertEqual(request.status_code, 401)
    
    def test_make_user_staff_not_staff(self):
        self.apiclient.force_authenticate(user=self.no_staff_user)
        data = json.dumps({
            'is_staff': True,
        })
        request = self.apiclient.put(self.url + str(self.user.id), data, content_type='application/json')
        self.assertEqual(request.status_code, 403)
    
    def test_make_user_staff_staff(self):
        data = json.dumps({
            'is_staff': True,
        })
        request = self.apiclient.put(self.url + str(self.user.id), data, content_type='application/json')
        self.assertEqual(request.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)
    
    def test_make_user_not_staff(self):
        data = json.dumps({
            'is_staff': False,
        })
        request = self.apiclient.put(self.url + str(self.user.id), data, content_type='application/json')
        self.assertEqual(request.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_staff)
    
    def test_make_user_staff_not_found(self):
        data = json.dumps({
            'is_staff': True,
        })
        request = self.apiclient.put(self.url + str(uuid.uuid4()), data, content_type='application/json')
        self.assertEqual(request.status_code, 404)
    
    def test_make_user_staff_no_data(self):
        request = self.apiclient.put(self.url + str(self.user.id), content_type='application/json')
        self.assertEqual(request.status_code, 400)
    
    def test_make_user_staff_no_id(self):
        data = json.dumps({
            'is_staff': True,
        })
        request = self.apiclient.put('/api/v1/user/staff/', data, content_type='application/json')
        self.assertEqual(request.status_code, 400)