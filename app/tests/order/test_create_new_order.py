from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate, APIClient
from core.models import User, Product, Order
from order.views import OrderViewSet
import json
import uuid
    

class Create_new_order(TestCase): 
    def setUp(self):
        self.factory = RequestFactory()
        self.balance = 2000
        self.user = User.objects.create(email='test@example.com', name='Test User', is_staff=True, balance=self.balance)
        self.quantity1 = 10
        self.product1 = Product.objects.create(name='Test Product',
                                              price=1000, quantity=self.quantity1, description='M Test product ', size='M', user=self.user, category='Shorts',
                                              color='Red')
        self.product2 = Product.objects.create(name='Test Product',
                                              price=1000, quantity=self.quantity1, description='S red product', size='S', user=self.user, category='Shorts',
                                              color='Red')
        self.product3 = Product.objects.create(name='Test Product',
                                              price=1000, quantity=self.quantity1, description='S Blue product', size='S', user=self.user, category='Shorts',
                                              color='Blue')
        self.product_discount = Product.objects.create(name='Test Product',
                                              price=1000, quantity=self.quantity1, description='M Test product ', size='M', user=self.user, category='Shorts',
                                              color='Red', discount_percentage=50)
        self.product_discount_2 = Product.objects.create(name='Test Product',
                                              price=1000, quantity=self.quantity1, description='M Test product ', size='M', user=self.user, category='Shorts',
                                              color='Red', discount_percentage=90)
        self.apiclient = APIClient()
        self.url = '/api/v1/orders/create_order_new/'
        self.apiclient.force_authenticate(user=self.user)
        self.street_address = 'Test Street'
        self.city = 'Test City'
        self.zip_code = '123456'
        self.country = 'Test Country'
        self.payment_mode = "COD"
    
    def test_create_order_new_correctly(self):
              
        
        data = {
            "street_address": self.street_address,
            "city": self.city,
            "zip_code": self.zip_code,
            "country": self.country,
            "payment_mode": self.payment_mode,
            "cart": [
            {
                "id": str(self.product1.id),
                "quantity": 1,
            },
            {
                "id": str(self.product2.id),
                "quantity": 1,
            }
        ]
        }
        
        response = self.apiclient.post(self.url, json.dumps(data), content_type='application/json')
       
        self.assertEqual(response.status_code, 201)
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.product1.quantity, self.quantity1 - 1)
        self.assertEqual(self.product2.quantity, self.quantity1 - 1)
        self.assertEqual(self.user.balance, self.balance - 2000)
        
        order = Order.objects.get(id=response.data['data']['id'])
        self.assertEqual(order.total_amount, 2000)
        self.assertEqual(order.street_address, self.street_address)
        self.assertEqual(order.city, self.city)
        self.assertEqual(order.zip_code, self.zip_code)
        self.assertEqual(order.country, self.country)
        self.assertEqual(order.payment_mode, self.payment_mode)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.order_items.count(), 2)
    
    def test_create_order_new_no_authenticated(self):
        
        self.apiclient.force_authenticate(user=None)
        data = {
            "street_address": self.street_address,
            "city": self.city,
            "zip_code": self.zip_code,
            "country": self.country,
            "payment_mode": self.payment_mode,
            "cart": [
            {
                "id": str(self.product1.id),
                "quantity": 1,
            },
            {
                "id": str(self.product2.id),
                "quantity": 1,
            }
        ]
        }
        
        response = self.apiclient.post(self.url, json.dumps(data), content_type='application/json')
        
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.user.refresh_from_db()
        
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['error'], 'Not authenticated')
        self.assertEqual(self.product1.quantity, self.quantity1)
        self.assertEqual(self.product2.quantity, self.quantity1)
        self.assertEqual(self.user.balance, self.balance)
    
    def test_create_order_new_no_street_address(self):
            
        data = {
            "city": self.city,
            "zip_code": self.zip_code,
            "country": self.country,
            "payment_mode": self.payment_mode,
            "cart": [
            {
                "id": str(self.product1.id),
                "quantity": 1,
            },
            {
                "id": str(self.product2.id),
                "quantity": 1,
            }
        ]
        }
        
        response = self.apiclient.post(self.url, json.dumps(data), content_type='application/json')
        
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.user.refresh_from_db()
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Street address is required')
        self.assertEqual(self.product1.quantity, self.quantity1)
        self.assertEqual(self.product2.quantity, self.quantity1)
        self.assertEqual(self.user.balance, self.balance)
            
    def test_create_order_new_no_city(self):
                
        data = {
            "street_address": self.street_address,
            "zip_code": self.zip_code,
            "country": self.country,
            "payment_mode": self.payment_mode,
            "cart": [
            {
                "id": str(self.product1.id),
                "quantity": 1,
            },
            {
                "id": str(self.product2.id),
                "quantity": 1,
            }
        ]
        }
        
        response = self.apiclient.post(self.url, json.dumps(data), content_type='application/json')
        
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.user.refresh_from_db()
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'City is required')
        self.assertEqual(self.product1.quantity, self.quantity1)
        self.assertEqual(self.product2.quantity, self.quantity1)
        self.assertEqual(self.user.balance, self.balance)
        
    def test_create_order_new_no_zip_code(self):
                    
        data = {
            "street_address": self.street_address,
            "city": self.city,
            "country": self.country,
            "payment_mode": self.payment_mode,
            "cart": [
            {
                "id": str(self.product1.id),
                "quantity": 1,
            },
            {
                "id": str(self.product2.id),
                "quantity": 1,
            }
        ]
        }
        
        response = self.apiclient.post(self.url, json.dumps(data), content_type='application/json')
        
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.user.refresh_from_db()
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Zip code is required')
        self.assertEqual(self.product1.quantity, self.quantity1)
        self.assertEqual(self.product2.quantity, self.quantity1)
        self.assertEqual(self.user.balance, self.balance)
        
    def test_create_order_new_no_country(self):
        
        data = {
            "street_address": self.street_address,
            "city": self.city,
            "zip_code": self.zip_code,
            "payment_mode": self.payment_mode,
            "cart": [
            {
                "id": str(self.product1.id),
                "quantity": 1,
            },
            {
                "id": str(self.product2.id),
                "quantity": 1,
            }
        ]
        }
        
        response = self.apiclient.post(self.url, json.dumps(data), content_type='application/json')
        
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.user.refresh_from_db()
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Country is required')
        self.assertEqual(self.product1.quantity, self.quantity1)
        self.assertEqual(self.product2.quantity, self.quantity1)
        self.assertEqual(self.user.balance, self.balance)
        
    def test_create_order_new_no_payment_mode(self):
                            
        data = {
            "street_address": self.street_address,
            "city": self.city,
            "zip_code": self.zip_code,
            "country": self.country,
            "cart": [
            {
                "id": str(self.product1.id),
                "quantity": 1,
            },
            {
                "id": str(self.product2.id),
                "quantity": 1,
            }
        ]
        }
        
        response = self.apiclient.post(self.url, json.dumps(data), content_type='application/json')
        
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.user.refresh_from_db()
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Payment mode is required')
        self.assertEqual(self.product1.quantity, self.quantity1)
        self.assertEqual(self.product2.quantity, self.quantity1)
        self.assertEqual(self.user.balance, self.balance)
    
    def test_create_order_new_no_cart(self):
                                
        data = {
            "street_address": self.street_address,
            "city": self.city,
            "zip_code": self.zip_code,
            "country": self.country,
            "payment_mode": self.payment_mode,
        }
        
        response = self.apiclient.post(self.url, json.dumps(data), content_type='application/json')
        
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.user.refresh_from_db()
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Cart is empty')
        self.assertEqual(self.product1.quantity, self.quantity1)
        self.assertEqual(self.product2.quantity, self.quantity1)
        self.assertEqual(self.user.balance, self.balance)  
        
    def test_create_order_new_empty_cart(self):
                                        
        data = {
            "street_address": self.street_address,
            "city": self.city,
            "zip_code": self.zip_code,
            "country": self.country,
            "payment_mode": self.payment_mode,
            "cart": []
        }
        
        response = self.apiclient.post(self.url, json.dumps(data), content_type='application/json')
        
        self.product1.refresh_from_db()
        self.product2.refresh_from_db()
        self.user.refresh_from_db()
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Cart is empty')
        self.assertEqual(self.product1.quantity, self.quantity1)
        self.assertEqual(self.product2.quantity, self.quantity1)
        self.assertEqual(self.user.balance, self.balance)
    
    def test_create_order_new_product_not_found(self):
                                                
            data = {
                "street_address": self.street_address,
                "city": self.city,
                "zip_code": self.zip_code,
                "country": self.country,
                "payment_mode": self.payment_mode,
                "cart": [
                {
                    "id": str(uuid.uuid4()),
                    "quantity": 1,
                },
                {
                    "id": str(uuid.uuid4()),
                    "quantity": 1,
                }
            ]
            }
            
            response = self.apiclient.post(self.url, json.dumps(data), content_type='application/json')
            
            self.product1.refresh_from_db()
            self.product2.refresh_from_db()
            self.user.refresh_from_db()
            
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.data['error'], 'Product not found')
            self.assertEqual(self.product1.quantity, self.quantity1)
            self.assertEqual(self.product2.quantity, self.quantity1)
            self.assertEqual(self.user.balance, self.balance)   
    def test_create_order_new_not_enough_stock(self):
                                                    
            data = {
                "street_address": self.street_address,
                "city": self.city,
                "zip_code": self.zip_code,
                "country": self.country,
                "payment_mode": self.payment_mode,
                "cart": [
                {
                    "id": str(self.product1.id),
                    "quantity": 11,
                },
                {
                    "id": str(self.product2.id),
                    "quantity": 11,
                }
            ]
            }
            
            response = self.apiclient.post(self.url, json.dumps(data), content_type='application/json')
            
            self.product1.refresh_from_db()
            self.product2.refresh_from_db()
            self.user.refresh_from_db()
            
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data['error'], 'Not enough stock')
            self.assertEqual(self.product1.quantity, self.quantity1)
            self.assertEqual(self.product2.quantity, self.quantity1)
            self.assertEqual(self.user.balance, self.balance)
    def test_create_order_new_not_enough_balance(self):
                                                        
            data = {
                "street_address": self.street_address,
                "city": self.city,
                "zip_code": self.zip_code,
                "country": self.country,
                "payment_mode": self.payment_mode,
                "cart": [
                {
                    "id": str(self.product1.id),
                    "quantity": 1,
                },
                {
                    "id": str(self.product2.id),
                    "quantity": 1,
                }
            ]
            }
            
            self.user.balance = 1999
            self.user.save()
            response = self.apiclient.post(self.url, json.dumps(data), content_type='application/json')
            
            self.product1.refresh_from_db()
            self.product2.refresh_from_db()
            self.user.refresh_from_db()
            
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.data['error'], 'Not enough balance')
            self.assertEqual(self.product1.quantity, self.quantity1)
            self.assertEqual(self.product2.quantity, self.quantity1)
            self.assertEqual(self.user.balance, 1999)
    
    def test_create_order_new_enough_balance(self):
                                                            
            data = {
                "street_address": self.street_address,
                "city": self.city,
                "zip_code": self.zip_code,
                "country": self.country,
                "payment_mode": self.payment_mode,
                "cart": [
                {
                    "id": str(self.product1.id),
                    "quantity": 1,
                },
                {
                    "id": str(self.product2.id),
                    "quantity": 1,
                }
            ]
            }
            
            self.user.balance = 2000
            self.user.save()
            response = self.apiclient.post(self.url, json.dumps(data), content_type='application/json')
            
            self.product1.refresh_from_db()
            self.product2.refresh_from_db()
            self.user.refresh_from_db()
            
            self.assertEqual(response.status_code, 201)
            self.assertEqual(self.product1.quantity, self.quantity1 - 1)
            self.assertEqual(self.product2.quantity, self.quantity1 - 1)
            self.assertEqual(self.user.balance, 0)
                                              
    def test_create_order_with_discount(self):
        data = {
            "street_address": self.street_address,
            "city": self.city,
            "zip_code": self.zip_code,
            "country": self.country,
            "payment_mode": self.payment_mode,
            "cart": [
            {
                "id": str(self.product_discount.id),
                "quantity": 1,
            }
        ]
        }
        
        response = self.apiclient.post(self.url, json.dumps(data), content_type='application/json')
        self.user.refresh_from_db()
        
        
        # buscamos la orden creada
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['data']['total_amount'], 500)
        self.assertEqual(self.user.balance, 1500)
        
        data = {
            "street_address": self.street_address,
            "city": self.city,
            "zip_code": self.zip_code,
            "country": self.country,
            "payment_mode": self.payment_mode,
            "cart": [
            {
                "id": str(self.product_discount.id),
                "quantity": 1,
            }, {
                "id": str(self.product_discount_2.id),
                "quantity": 2,
            }
        ]
        }
        response = self.apiclient.post(self.url, json.dumps(data), content_type='application/json')
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['data']['total_amount'], 700) # ambos productos valen 1000. el primero tiene 50% de descuento y el segundo tiene 90% de descuento
        self.assertEqual(self.user.balance, 1500-700)
        
