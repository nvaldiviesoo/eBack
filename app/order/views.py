"""
Order views
"""

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from core.models import Order, OrderItem, Product
from .serializers import OrderSerializer, OrderItemSerializer

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
                product = Product.objects.get(id=item.get('product_id'))

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
  
