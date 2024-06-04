from django.test import TestCase, RequestFactory
from rest_framework.test import force_authenticate, APIClient
from core.models import User, Product
from product.views import ProductViewSet
import json

class Product_tests(TestCase): # Cambiar el nombre en caso de crear más clases.
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(email='test@example.com', name='Test User')
        self.product = Product.objects.create(name='Test Product',
                                              price=1000, quantity=10, description='Test Description', size='M', user=self.user, category='Shorts',
                                              )
        self.apiclient = APIClient()

        
    def test_get_products_correctly(self):
        request = self.factory.get('/api/v1/products/get_products/')
        # force_authenticate(request, user=self.user)
        view = ProductViewSet.as_view({'get': 'get_products'})
        response = view(request)
        
        # Comprobamos que exista solo un elemento en la respuesta y que sea el creado arriba
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['quantity'], 10)
        self.assertEqual(response.data["data"][0]["id"], str(self.product.id))
        self.assertEqual(response.status_code, 200)
        
        self.client.get('/api/v1/products/get_products/')
        
    def test_get_products_correctly_2(self):

        response = self.client.get('/api/v1/products/get_products/')
        
        # Comprobamos que exista solo un elemento en la respuesta y que sea el creado arriba
        # Por alguna razón, este test le cambia el ID al producto creado.    
        self.assertEqual(len(response.data['data']), 1)
        self.assertEqual(response.data['data'][0]['quantity'], 10)
        self.assertEqual(response.data["data"][0]["name"], str(self.product.name))
        self.assertEqual(response.status_code, 200)
        
            
    def test_update_product_name(self):
        data = json.dumps({
            'id': str(self.product.id),
            'name': 'New name'
        }) 
        url = '/api/v1/products/'
        
        response = self.apiclient.put(url, data, content_type='application/json')
                    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]['name'], 'New name')

    #TODO: hacer más .py para cada uno de los endpoints, así se puede dejar una self.URL y se vuelve más fácil de leer

    def test_update_product_description(self):
        data = json.dumps({
            'id': str(self.product.id),
            'description': 'New description for the product'
        }) 
        url = '/api/v1/products/'
        
        response = self.apiclient.put(url, data, content_type='application/json')
                    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]['description'], 'New description for the product')
        
    def test_update_product_price(self):
        self.assertEqual(self.product.price, 1000)
        data = json.dumps({
            'id': str(self.product.id),
            'price': 500
        }) 
        url = '/api/v1/products/'
        
        response = self.apiclient.put(url, data, content_type='application/json')
                    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]['price'], 500)
        
    def test_update_product_price_negative(self):
        self.assertEqual(self.product.price, 1000)
        data = json.dumps({
            'id': str(self.product.id),
            'price': -1
        })
        
        url = '/api/v1/products/'
        response = self.apiclient.put(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['price'][0], 'Ensure this value is greater than or equal to 0.')
    
    def test_update_product_price_to_0(self):
        self.assertEqual(self.product.price, 1000)
        data = json.dumps({
            'id': str(self.product.id),
            'price': 0
        })
        
        url = '/api/v1/products/'
        response = self.apiclient.put(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['price'], 0)
    
    def test_update_product_quantity(self):
        self.assertEqual(self.product.quantity, 10)
        data = json.dumps({
            'id': str(self.product.id),
            'quantity': 5
        }) 
        url = '/api/v1/products/'
        
        response = self.apiclient.put(url, data, content_type='application/json')
                    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]['quantity'], 5)
    
    def test_update_product_quantity_negative(self):
        self.assertEqual(self.product.quantity, 10)
        data = json.dumps({
            'id': str(self.product.id),
            'quantity': -1
        })
        
        url = '/api/v1/products/'
        response = self.apiclient.put(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['quantity'][0], 'Ensure this value is greater than or equal to 0.')
        
    def test_update_product_quantity_to_0(self):
        self.assertEqual(self.product.quantity, 10)
        data = json.dumps({
            'id': str(self.product.id),
            'quantity': 0
        })
        
        url = '/api/v1/products/'
        response = self.apiclient.put(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['quantity'], 0)
    
    def test_update_product_size(self):
        self.assertEqual(self.product.size, 'M')
        data = json.dumps({
            'id': str(self.product.id),
            'size': 'S'
        }) 
        url = '/api/v1/products/'
        response = self.apiclient.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]['size'], 'S')
    
    def test_update_product_size_invalid(self):
        self.assertEqual(self.product.size, 'M')
        data = json.dumps({
            'id': str(self.product.id),
            'size': 'FAIL'
        }) 
        url = '/api/v1/products/'
        response = self.apiclient.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['size'][0], '"FAIL" is not a valid choice.')
        
    def test_update_product_category(self):
        self.assertEqual(self.product.category, 'Shorts')
        data = json.dumps({
            'id': str(self.product.id),
            'category': 'Shorts'
        }) 
        url = '/api/v1/products/'
        response = self.apiclient.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]['category'], 'Shorts')
    
    def test_update_product_category_invalid(self):
        self.assertEqual(self.product.category, 'Shorts')
        data = json.dumps({
            'id': str(self.product.id),
            'category': 'FAIL'
        }) 
        url = '/api/v1/products/'
        response = self.apiclient.put(url, data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['category'][0], '"FAIL" is not a valid choice.')
        

    def test_stock_update(self):
        self.assertEqual(self.product.quantity, 10)
        data = json.dumps({
            'id': str(self.product.id),
            'quantity': 5
        }) 
        url = '/api/v1/products/stock_update/'
        
        response = self.apiclient.put(url, data, content_type='application/json')
                    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]['quantity'], 5)
        
    def test_stock_update_negative(self):
        self.assertEqual(self.product.quantity, 10)
        data = json.dumps({
            'id': str(self.product.id),
            'quantity': -1
        })
        
        url = '/api/v1/products/stock_update/'
        response = self.apiclient.put(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['quantity'][0], 'Ensure this value is greater than or equal to 0.')
        
    def test_stock_update_to_0(self):
        self.assertEqual(self.product.quantity, 10)
        data = json.dumps({
            'id': str(self.product.id),
            'quantity': 0
        })
        
        url = '/api/v1/products/stock_update/'
        response = self.apiclient.put(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['quantity'], 0)
        
    def test_stock_update_not_parameter(self):
        self.assertEqual(self.product.quantity, 10)
        data = json.dumps({
            'id': str(self.product.id),
            'price': 0
        })
        
        url = '/api/v1/products/stock_update/'
        response = self.apiclient.put(url, data, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Quantity is required.')
    
    def test_stock_update_change_other_parameters(self):
        self.assertEqual(self.product.price, 1000)
        self.assertEqual(self.product.quantity, 10)
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.description, 'Test Description')
        self.assertEqual(self.product.size, 'M')
        self.assertEqual(self.product.category, 'Shorts')
        self.assertEqual(self.product.color, 'Other')
        data = json.dumps({
            'id': str(self.product.id),
            'quantity': 25,
            'price': 500,
            'name' : 'Not a name',
            'description': 'Not a description',
            'size': 'Not a size',
            'category': 'Not a category',
            'color': 'Not a color',            
        }) 
        url = '/api/v1/products/stock_update/'
        
        response = self.apiclient.put(url, data, content_type='application/json')
                    
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["data"]['quantity'], 25)
        self.assertEqual(response.data["data"]['price'], 1000)
        self.assertEqual(response.data["data"]['name'], 'Test Product')
        self.assertEqual(self.product.description, 'Test Description')
        self.assertEqual(self.product.size, 'M')
        self.assertEqual(self.product.category, 'Shorts')
        self.assertEqual(self.product.color, 'Other')
        

        