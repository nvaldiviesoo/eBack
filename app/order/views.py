"""
Order views
"""

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from core.models import Order, OrderItem, Product, User
from .serializers import OrderSerializer, OrderItemSerializer
from .service_order import authenticate_staff

class OrderViewSet(ModelViewSet):

    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(methods=['post'], detail=False)
    def create_order(self, request):
        user = request.user
        order_items = request.data.get('order_items')

        if order_items and len(order_items) == 0:
            return Response({'error': 'Order items cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)

        else:

            total_amount = sum(item.get('price') * item.get('quantity') for item in order_items)

            order = Order.objects.create(
                user=user,
                street_address=request.data.get('street_address'),
                city=request.data.get('city'),
                zip_code=request.data.get('zip_code'),
                country=request.data.get('country'),
                total_amount=total_amount,
            )

            for item in order_items:
                try :
                    product = Product.objects.get(id=item.get('product_id'))
                except Product.DoesNotExist:
                    return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
                
                item = OrderItem.objects.create(
                    order=order,
                    name=product.name,
                    quantity=item.get('quantity'),
                    price=item.get('price'),
                )

                product.stock -= item.quantity
                product.save()

            serializer = self.serializer_class(order, many=True)
            return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)
        
    @action(methods=['post'], detail=False)
    def create_order_new(self, request):
        # Validamos que exista un usuario haciendo la compra. Si no, no es necesario 
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Revisar que existan los parametros necesarios antes de hacer la compra
        street_address = request.data.get('street_address')
        city = request.data.get('city')
        zip_code = request.data.get('zip_code')
        country = request.data.get('country')
        payment_mode = request.data.get('payment_mode')
        
        if not street_address:
            return Response({'error': 'Street address is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not city:
            return Response({'error': 'City is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not zip_code:
            return Response({'error': 'Zip code is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not country:
            return Response({'error': 'Country is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not payment_mode:
            return Response({'error': 'Payment mode is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Extraemos el carrito
        cart = request.data.get('cart')
        if cart is None:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        if len(cart) == 0:
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validamos que haya stock suficiente y mientras tanto, vamos sumando el precio.
        total_amount = 0
        for item in cart:
            try :
                product = Product.objects.get(id=item["id"])
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if product is None:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
            
            if product.quantity < item['quantity']:
                return Response({'error': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)
            
            total_amount += item['quantity'] * (product.price * ((100 - product.discount_percentage) / 100))
        
        # Comprobamos el dinero del usuario sea mayor o igual al total de la compra
        user = request.user
        if user.balance < total_amount:
            return Response({'error': 'Not enough balance'}, status=status.HTTP_400_BAD_REQUEST)
        user.balance -= total_amount
        user.save()
        
        # Creamos la orden
        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            payment_mode=payment_mode,
            street_address=street_address,
            city=city,
            zip_code=zip_code,
            country=country,    
            payment_status='PAID'        
        )
        
        # Creamos los items de la orden
        for item in cart:
            product = Product.objects.get(id=item["id"])
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item['quantity'],
                price=product.price * ((100 - product.discount_percentage) / 100),
            )
            product.quantity -= item['quantity']
            product.save()
        
        # retornamos los orderitems serializados
        
        serializer = self.serializer_class(order)
        
        return Response({'data': serializer.data, "Balance": user.balance}, status=status.HTTP_201_CREATED)
        
        