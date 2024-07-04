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
            'name': 'Test User edit',
            'is_superuser': True
        })

        request = self.apiclient.put(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 403)
    
    def test_edit_profile_no_name(self):
        data = json.dumps({})

        request = self.apiclient.put(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 400)
    
    def test_edit_profile_unauthorized(self):
        self.apiclient.force_authenticate(user=None)
        data = json.dumps({
            'name': 'Test User edit'
        })

        request = self.apiclient.put(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 403)
    
    def test_edit_profile_name_min_length(self):
        data = json.dumps({
            'name': 'Test'
        })

        request = self.apiclient.put(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 400)
    
    def test_edit_profile_name_max_length(self):
        data = json.dumps({
            'name': 'qwertyuioplkjhgfdsazxcvbnmnbvcxzasdfghjkloiuytrewqwertyuioplkjhgfdsazxcvbnmnbvcxzasdfghjkloiuytrew'
        })

        request = self.apiclient.put(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 400)
    
    def test_edit_profile_birth_date(self):
        data = json.dumps({
            'name': 'Test User edit',	
            'birth_date': '2021-01-01'
        })

        request = self.apiclient.put(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 200)

    def test_edit_profile_birth_date_empty(self):
        data = json.dumps({
            'name': 'Test User edit',	
            'birth_date': ''
        })

        request = self.apiclient.put(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 400)

    def test_edit_profile_birth_date_invalid_format(self):
        data = json.dumps({
            'name': 'Test User edit',	
            'birth_date': '01-01-2021'
        })

        request = self.apiclient.put(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 400)

    def test_edit_profile_birth_date_invalid_date(self):
        data = json.dumps({
            'name': 'Test User edit',	
            'birth_date': '2021-13-01'
        })

        request = self.apiclient.put(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 400)

    def test_edit_profile_birth_date_invalid_type(self):
        data = json.dumps({
            'name': 'Test User edit',	
            'birth_date': 20210101
        })

        request = self.apiclient.put(self.url, data, content_type='application/json')
        self.assertEqual(request.status_code, 400)
