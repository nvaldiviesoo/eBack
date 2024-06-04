from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate
from core.models import User, Product
from product.views import ProductViewSet

class Product_tests(TestCase): # Cambiar el nombre en caso de crear más clases.
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(email='test@example.com', name='Test User')

    # def test_get(self):
    #     request = self.factory.get('/user/me')
    #     force_authenticate(request, user=self.user)
    #     view = ProductViewSet.as_view({'get': 'me'})
    #     response = view(request)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.data['data']['email'], self.user.email)