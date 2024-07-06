from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate, APIClient
from core.models import User, Product
import json
import uuid

class Product_tests(TestCase): # Cambiar el nombre en caso de crear más clases.
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(email='test@example.com', name='Test User', is_staff=True)
        self.product = Product.objects.create(name='Test Product',
                                              price=1000, quantity=10, description='Test Description', size='M', user=self.user, category='Shorts', color='Red'
                                              )
        self.apiclient = APIClient()
        self.url = '/api/v1/products/edit_product_discount/'
        self.apiclient.force_authenticate(user=self.user)
    
    def test_edit_product_discount_correct(self):
        data = {'id': self.product.id, 'discount': 5}
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"][0]["discount_percentage"], 5)
    
    def test_edit_product_discount_same_color(self):
        data = {'id': self.product.id, 'discount': 5}
        product_2 = Product.objects.create(name='Test Product',
                                           price=1000, quantity=10, description='Test Description', size='M', user=self.user, category='Shorts', discount_percentage=100, color='Red')
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"][0]["discount_percentage"], 5)
        self.assertEqual(response.data["data"][1]["discount_percentage"], 5)
    
    def test_edit_product_discount_same_color_different_discount(self):
        data = {'id': self.product.id, 'discount': 5}
        product_2 = Product.objects.create(name='Test Product',
                                           price=1000, quantity=10, description='Test Description', size='M', user=self.user, category='Shorts', discount_percentage=100, color='Blue')
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"][0]["discount_percentage"], 5)
        self.assertEqual(len(response.data["data"]), 1) # Colores distintos no rompe el producto
        
    def test_edit_product_not_found(self):
        data = {'id': uuid.uuid4(), 'discount': 5}
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["error"], "Product not found")
    
    def test_edit_product_no_discount(self):
        data = {'id': self.product.id}
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Discount is required.")
    
    def test_edit_product_discount_negative(self):
        data = {'id': self.product.id, 'discount': -5}
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Discount must be between 0 and 100.")
    
    def test_edit_product_discount_over_100(self):
        data = {'id': self.product.id, 'discount': 101}
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Discount must be between 0 and 100.")
    
    def test_edit_product_discount_not_int(self):
        data = {'id': self.product.id, 'discount': 'a'}
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Discount must be an integer.")
        
    def test_edit_product_discount_id_not_uuid(self):
        data = {'id': 'a', 'discount': 5}
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["error"], "ID must be a valid ID.")