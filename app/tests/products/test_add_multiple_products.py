from django.test import TestCase, RequestFactory
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
        self.apiclient.force_authenticate(user=self.staff)
        self.url = '/api/v1/products/add_multiple_products/'
        
        self.name = "Test product"
        self.description = "Test description"
        self.price = 1000
        self.quantity = 10
        self.category = "Shorts"
        self.color = "Red"
    
    def test_add_product_valid(self):
        
        data ={
        "products": [
        {
        "name": "Test Add Multiple Products",
        "description": "First item in this test",
        "price": 1111,
        #"image":"None",
        "category": "Sports Bra",
        "gender": "Female",
        "size": "S", 
        "color": "Red", 
        "quantity": 10
        },
        {
        "name": "Test Add Multiple Products",
        "description": "First item in this test",
        "price": 1111,
        #"image":"Null",
        "category": "Sports Bra",
        "gender": "Female",
        "size": "XS", 
        "color": "Red", 
        "quantity": 10
        },
        {
        "name": "Test Add Multiple Products",
        "description": "First item in this test",
        "price": 1111,
        #"image":"Null",
        "category": "Sports Bra",
        "gender": "Female",
        "size": "L", 
        "color": "Red", 
        "quantity": 10
        }
            ]}
        
        response = self.apiclient.post(self.url, json.dumps(data), content_type="application/json")        

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["data"], [{'name': 'Test Add Multiple Products', 'error': 'Producto creado sin errores'}, 
                                                 {'name': 'Test Add Multiple Products', 'error': 'Producto creado sin errores'}, 
                                                 {'name': 'Test Add Multiple Products', 'error': 'Producto creado sin errores'}])
        # ahora revisamos que en la base de datos se crearon
        self.assertEqual(Product.objects.count(), 4)
        query = Product.objects.filter(name='Test Add Multiple Products')
        self.assertEqual(query.count(), 3)
        self.assertEqual(query[0].size, 'S')
        self.assertEqual(query[1].size, 'XS')
        self.assertEqual(query[2].size, 'L')
    
    def test_add_one_invalid_product(self):
        self.apiclient.force_authenticate(self.staff)
        data ={
        "products": [
        {
        "name": "Test Add Multiple Products",
        "description": "First item in this test",
        "price": 1111,
        #"image":"None",
        "category": "Sports Bra",
        "gender": "Female",
        "size": "S", 
        "color": "Red", 
        "quantity": 10
        },
        {
        "name": "Test Add Multiple Products",
        "description": "First item in this test",
        "price": 1111,
        #"image":"Null",
        "category": "Sports Bra",
        "gender": "Female",
        "size": "S", 
        "color": "Red", 
        "quantity": 10
        },
        {
        "name": "Test Add Multiple Products",
        "description": "First item in this test",
        "price": 1111,
        #"image":"Null",
        "category": "Sports Bra",
        "gender": "Female",
        "size": "L", 
        "color": "Red", 
        "quantity": 10
        }
            ]}

        response = self.apiclient.post(self.url, json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["data"], [{'name': 'Test Add Multiple Products', 'error': 'Producto creado sin errores'}, 
                                                 {'name': 'Test Add Multiple Products', 'error': 'Ya existe este item'}, 
                                                 {'name': 'Test Add Multiple Products', 'error': 'Producto creado sin errores'}])
        self.assertEqual(Product.objects.count(), 3)
        query = Product.objects.filter(name='Test Add Multiple Products')
        self.assertEqual(query.count(), 2)
        self.assertEqual(query[0].size, 'S')
        self.assertEqual(query[1].size, 'L')


    def test_add_multiple_invalid_products(self):
        
        data ={
        "products": [
        {
        "name": "Very very very very very very very very very very very very very very very very very very very long name",
        "description": "First item in this test",
        "price": 1111,
        #"image":"None",
        "category": "Sports Bra",
        "gender": "Female",
        "size": "S", 
        "color": "Red", 
        "quantity": 10
        },
        {
        "name": "na", #short name
        "description": "Second item in this test",
        "price": 1111,
        #"image":"None",
        "category": "Sports Bra",
        "gender": "Female",
        "size": "S", 
        "color": "Red", 
        "quantity": 10
        },
        {
        "name": "Test Add Multiple Products",
        "description": "Third item in this test",
        "price": -1, #negative price
        #"image":"Null",
        "category": "Sports Bra",
        "gender": "Female",
        "size": "XS", 
        "color": "Red", 
        "quantity": 10
        },
        {
        "name": "Test Add Multiple Products",
        "description": "First item in this test",
        "price": 1111,
        #"image":"Null",
        "category": "Invalid Category",
        "gender": "Female",
        "size": "L", 
        "color": "Red", 
        "quantity": 10
        },
        {
        "name": "Test Add Multiple Products",
        "description": "First item in this test",
        "price": 1111,
        #"image":"Null",
        "category": "Sports Bra",
        "gender": "who cares", #invalid
        "size": "L", 
        "color": "Red", 
        "quantity": 10
        },
        {
        "name": "Test Add Multiple Products",
        "description": "First item in this test",
        "price": 1111,
        #"image":"Null",
        "category": "Sports Bra",
        "gender": "Female",
        "size": "P", #invalid
        "color": "Red", 
        "quantity": 10
        },
        {
        "name": "Test Add Multiple Products",
        "description": "First item in this test",
        "price": 1111,
        #"image":"Null",
        "category": "Sports Bra",
        "gender": "Female",
        "size": "L", 
        "color": "Is mayonnaise an instrument?", #invalid
        "quantity": 10
        },
        {
        "name": "Test Add Multiple Products",
        "description": "First item in this test",
        "price": 1111,
        #"image":"Null",
        "category": "Sports Bra",
        "gender": "Female",
        "size": "L", 
        "color": "Red", 
        "quantity": -10
        },
        {
        "name": "Test Add Multiple Products",
        "description": "First item in this test",
        "price": 1111,
        #"image":"None",
        "category": "Sports Bra",
        "gender": "Female",
        "size": "S", 
        "color": "Red", 
        "quantity": 10
        }
            ]
        }
        
        response = self.apiclient.post(self.url, json.dumps(data), content_type="application/json")     

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data["data"], [{'name': None, 'error': 'Invalid name'}, 
                                                 {'name': None, 'error': 'Invalid name'}, 
                                                 {'name': 'Test Add Multiple Products', 'error': 'Invalid price'}, 
                                                 {'name': 'Test Add Multiple Products', 'error': 'Invalid category'},
                                                 {'name': 'Test Add Multiple Products', 'error': 'Invalid gender'},
                                                 {'name': 'Test Add Multiple Products', 'error': 'Invalid size'},
                                                 {'name': 'Test Add Multiple Products', 'error': 'Invalid color'},
                                                 {'name': 'Test Add Multiple Products', 'error': 'Invalid quantity'},
                                                 {'name': 'Test Add Multiple Products', 'error': 'Producto creado sin errores'}])
        # ahora revisamos que en la base de datos se crearon
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(Product.objects.filter(name='Test Add Multiple Products').count(), 1)
        