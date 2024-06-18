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
        self.apiclient = APIClient()
        self.url = '/api/v1/orders/edit_order_status/'
        self.apiclient.force_authenticate(user=self.user)
        self.street_address = 'Test Street'
        self.city = 'Test City'
        self.zip_code = '123456'
        self.country = 'Test Country'
        self.payment_mode = "COD"
        self.order = Order.objects.create(user=self.user, street_address=self.street_address, city=self.city, zip_code=self.zip_code, country=self.country, total_amount=2000, payment_mode=self.payment_mode)
    
    def test_edit_order(self):
            
        data = {'id': self.order.id, 'status': 'Delivered'}
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(self.order.status, 'Processing')
        self.assertEqual(response.data['data']['status'], 'Delivered')
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'Delivered')
    
    def test_edit_order_not_found(self):
                
        data = {'id': uuid.uuid4(), 'status': 'Delivered'}
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Order not found')
    
    def test_edit_order_no_id(self):
                
        data = {'status': 'Delivered'}
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'Order not found')
    
    def test_edit_order_no_status(self):
                    
        data = {'id': self.order.id}
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Status is required')
    
    def test_edit_order_invalid_status(self):
                            
        data = {'id': self.order.id, 'status': 'Invalid'}
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Invalid status')
    
    def test_edit_order_not_authorized(self):
        self.apiclient.force_authenticate(user=None)
        data = {'id': self.order.id, 'status': 'Delivered'}
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['error'], 'Not authorized')
    
    def test_edit_order_not_staff(self):
        self.user.is_staff = False
        self.user.save()
        data = {'id': self.order.id, 'status': 'Delivered'}
        response = self.apiclient.patch(self.url, data)
        
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['error'], 'Not authorized')