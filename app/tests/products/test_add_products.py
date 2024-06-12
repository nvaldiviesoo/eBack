from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate, APIClient
from core.models import User, Product
from product.views import ProductViewSet
import json
import uuid

class AddProduct(TestCase): 
    def setUp(self):
        self.factory = RequestFactory()
        self.staff = User.objects.create(email='staff@example.com', name='Test Staff', is_staff=True)
        self.user = User.objects.create(email='test@example.com', name='Test User', is_staff=False)
        self.product = Product.objects.create(name='Test Product',
                                              price=1000, quantity=10, description='Test Description', size='M', user=self.user, category='Shorts',
                                              color='Red')
        self.apiclient = APIClient()
        self.apiclient.force_authenticate(user=self.user)
        self.url = '/api/v1/products/add_product/'
    
    def test_add_product_valid(self):
        force_authenticate(self.staff)
        data = {'name': 'Test Product 2', 'price': 1000, 'quantity': 10, 'description': 'Test Description', 'size': 'M', 'category': 'Shorts', 'color': 'Red'}
        response = self.apiclient.post(self.url, data)
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['data']['name'], 'Test Product 2')
    
    def test_add_existing_product(self):
        force_authenticate(self.staff)
        data = {'name': 'Test Product', 'price': 1000, 'quantity': 10, 'description': 'Test Description', 'size': 'M', 'category': 'Shorts', 'color': 'Red'}
        response = self.apiclient.post(self.url, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['data']['error'], 'Ya existe este item')
    
    def test_add_invalid_product(self):
        force_authenticate(self.staff)
        data = {'name': 'Test Product 3', 'price': 1000, 'quantity': 10, 'description': 'Test Description', 'size': 'M', 'category': 'Shorts'}
        response = self.apiclient.post(self.url, data)
        
        self.assertEqual(response.status_code, 400)