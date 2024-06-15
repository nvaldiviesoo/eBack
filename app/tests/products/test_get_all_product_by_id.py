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
        self.apiclient = APIClient()
        self.url = '/api/v1/products/get_all_product_by_id/'
        self.apiclient.force_authenticate(user=self.user)
    
    def test_get_product_by_id(self):
        
        data = {'id': self.product1.id}
        response = self.apiclient.get(self.url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['name'], 'Test Product')
        self.assertEqual(response.data["quantity"]["Red"], {"S": self.quantity_2, "M": self.quantity_1})
        self.assertEqual(response.data["quantity"]["Blue"], {"S": self.quantity_3})
        self.assertDictEqual(response.data["ids"], {"Red": {"M": self.product1.id, "S": self.product2.id}, "Blue": {"S": self.product3.id}})
    
    def test_get_product_by_id_not_found(self):
        
        data = {'id': uuid.uuid4()}
        response = self.apiclient.get(self.url, data)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Product not found')
    
    def test_get_product_by_id_no_id(self):
        
        response = self.apiclient.get(self.url)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Product not found')
    
    def test_get_product_by_id_agregate_item(self):
        data = {'id': self.product1.id}
        response = self.apiclient.get(self.url, data)
        
        # Estos assert son solo para verificar que el endpoint funciona correctamente de antemano
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['name'], 'Test Product')
        self.assertEqual(response.data["quantity"]["Red"], {"S": self.quantity_2, "M": self.quantity_1})
        self.assertEqual(response.data["quantity"]["Blue"], {"S": self.quantity_3})
        
        #Probamos crear un nuevo producto para saber que el endpoint se actualiza correctamente
        new_product = Product.objects.create(name='Test Product',
                                              price=1000, quantity=1, description='Test Description', size='XL', user=self.user, category='Shorts',
                                              color='Blue')
        response = self.apiclient.get(self.url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['name'], 'Test Product')
        self.assertEqual(response.data["quantity"]["Red"], {"S": self.quantity_2, "M": self.quantity_1})
        self.assertEqual(response.data["quantity"]["Blue"], {"S": self.quantity_3, "XL": 1})
        self.assertDictEqual(response.data["ids"], {"Red": {"M": self.product1.id, "S": self.product2.id}, "Blue": {"S": self.product3.id, "XL": new_product.id}})
        
