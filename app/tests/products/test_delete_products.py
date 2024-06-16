from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate, APIClient
from core.models import User, Product
from product.views import ProductViewSet
import json
import uuid


class DeleteProduct(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.staff = User.objects.create(email='staff@example.com', name='Test Staff', is_staff=True)
        self.apiclient = APIClient()
        self.user = User.objects.create(email='test@example.com', name='Test User', is_staff=False)


    def test_delete_product_valid(self):
        self.apiclient.force_authenticate(self.staff)
        product = Product.objects.create(name='Test Product', price=1000, quantity=10, description='Test Description', size='M', user=self.user, category='Shorts', color='Red')
        url = f'/api/v1/products/delete_product_by_id/?id={product.id}'
        response = self.apiclient.delete(url)

        self.assertEqual(response.status_code, 200)
    
    def test_delete_product_no_valid(self):
        self.apiclient.force_authenticate(self.staff)
        id_false = uuid.uuid4()
        url = f'/api/v1/products/delete_product_by_id/?id={id_false}'
        response = self.apiclient.delete(url)

        self.assertEqual(response.status_code, 404)

    def test_delete_product_no_staff(self):
        self.apiclient.force_authenticate(self.user)
        product = Product.objects.create(name='Test Product', price=1000, quantity=10, description='Test Description', size='M', user=self.user, category='Shorts', color='Red')
        url = f'/api/v1/products/delete_product_by_id/?id={product.id}'
        response = self.apiclient.delete(url)

        self.assertEqual(response.status_code, 403)