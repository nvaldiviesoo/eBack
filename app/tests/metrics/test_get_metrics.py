from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate, APIClient
from core.models import User, Product, Order, OrderItem
from metrics.views import MetricsViewSet
import uuid

class GetMetricsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = APIClient()
        self.balance = 2000
        self.quantity1 = 10
        self.staff = User.objects.create(email='test@example.com', name='Test Staff', is_staff=True, balance=self.balance)
        self.user_1 = User.objects.create(email='test_1@example.com', name='Test User', is_staff=False, balance=self.balance)
        self.user_2 = User.objects.create(email='test_2@example.com', name='Test User2', is_staff=False, balance=self.balance)
        self.product1 = Product.objects.create(name='Test Product 1',
                                              price=1000, quantity=self.quantity1, description='M Test product ', size='M', user=self.staff, category='Shorts',
                                              color='Red')
        self.product2 = Product.objects.create(name='Test Product',
                                              price=1000, quantity=self.quantity1, description='S red product', size='S', user=self.staff, category='Shorts',
                                              color='Red')
        self.product3 = Product.objects.create(name='Test Product',
                                              price=1000, quantity=self.quantity1, description='S Blue product', size='S', user=self.staff, category='Shorts',
                                              color='Blue')
        self.street_address = 'Test Street'
        self.city = 'Test City'
        self.zip_code = '123456'
        self.country = 'Test Country'
        self.payment_mode = "COD"
        self.order_1 = Order.objects.create(user=self.user_1, street_address=self.street_address, 
                                     city=self.city, zip_code=self.zip_code, country=self.country, total_amount=3000)
        self.order_items_1 = {"cart": [
            {
                "id": str(self.product1.id),
                "quantity": 2,
            },
            {
                "id": str(self.product2.id),
                "quantity": 1,
            }]
            }
        for item in self.order_items_1["cart"]:
            product = Product.objects.get(id=item.get('id'))
            
            
            item = OrderItem.objects.create(
                order=self.order_1,
                product=product,
                quantity=item.get('quantity'),
                price=product.price * ((100 - product.discount_percentage) / 100),
            )

            product.quantity -= item.quantity
            product.quantity_sold += item.quantity
            product.save()
        self.order_2 = Order.objects.create(user=self.user_2, street_address=self.street_address, 
                                     city=self.city, zip_code=self.zip_code, country=self.country, total_amount=2000)
        self.order_items_2 = {"cart": [
            {
                "id": str(self.product1.id),
                "quantity": 1,
            },
            {
                "id": str(self.product3.id),
                "quantity": 1,
            }]
            }
        for item in self.order_items_2["cart"]:
            product = Product.objects.get(id=item.get('id'))
            
            
            item = OrderItem.objects.create(
                order=self.order_2,
                product=product,
                quantity=item.get('quantity'),
                price=product.price * ((100 - product.discount_percentage) / 100)
            )

            product.quantity -= item.quantity
            product.quantity_sold += item.quantity
            product.save()

    def test_get_metrics(self):
        self.client.force_authenticate(self.staff)
        url = '/api/v1/metrics/get_metrics/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['revenue'], 5000)
        self.assertEqual(response.data['data']['total_sold_products'], 5)
        self.assertEqual(response.data['data']['highest_sold_product'], 'Test Product 1')
        self.assertEqual(response.data['data']['average_order_value'], 2500)
        self.assertEqual(list(response.data['data']['price_distribution']), [1000, 1000, 1000])
    
    def test_get_metrics_unauthorized(self):
        self.client.force_authenticate(self.user_1)
        url = '/api/v1/metrics/get_metrics/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['error'], 'Not authorized')
