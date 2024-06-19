from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate, APIClient
from core.models import User, Product
from product.views import ProductViewSet
import json
import uuid

class Product_show_by_name(TestCase): 
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(email='test@example.com', name='Test User', is_staff=True)
        self.quantity_1 = 10
        self.quantity_2 = 9
        self.quantity_3 = 8
        self.product1 = Product.objects.create(name='Test Product',
                                              price=1000, quantity=self.quantity_1, description='Test Description', size='M', user=self.user, category='Shorts',
                                              color='Red')
        self.product2 = Product.objects.create(name='Test Product',
                                              price=1000, quantity=self.quantity_2, description='Test Description', size='S', user=self.user, category='Shorts',
                                              color='Red')
        self.product3 = Product.objects.create(name='Test Product',
                                              price=1000, quantity=self.quantity_3, description='Test Description', size='S', user=self.user, category='Shorts',
                                              color='Blue')
        self.product4 = Product.objects.create(name='Test Product 2',
                                              price=1000, quantity=self.quantity_3, description='Test Description', size='S', user=self.user, category='Shorts',
                                              color='Red')
        self.product5 = Product.objects.create(name='Test Product 3',
                                              price=1000, quantity=self.quantity_3, description='Test Description', size='S', user=self.user, category='Joggers',
                                              color='Red')
        self.apiclient = APIClient()
        self.url = '/api/v1/products/filter_products/'
        self.apiclient.force_authenticate(user=self.user)
    
    def test_get_product_by_name(self):
        response = self.apiclient.get(self.url, {'category': 'Shorts'})
        # print(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["data"]), 3) # se envian 3 elementos
        self.assertEqual(response.data["data"][0]["name"], 'Test Product')
        self.assertEqual(response.data["data"][1]["name"], 'Test Product')
        self.assertEqual(response.data["data"][2]["name"], 'Test Product 2')
    
    def test_not_category(self):
        response = self.apiclient.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], 'Category is required')
    
    def test_not_found(self):
        response = self.apiclient.get(self.url, {'category': 'Pants'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["error"], 'Products not found for this category')
    
