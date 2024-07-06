
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Avg


from core.models import Order, Product


class MetricsViewSet(ModelViewSet):

    @action(methods=['get'], detail=False)
    def get_metrics(self, request):
        user = request.user
        if user.is_staff:
            revenue = Order.objects.aggregate(total = Sum('total_amount'))['total']
            total_sold_products = Product.objects.aggregate(total = Sum('quantity_sold'))['total']
            highest_sold_product = Product.objects.order_by('-quantity_sold').first()
            average_order_value = int(Order.objects.aggregate(total = Avg('total_amount'))['total'])
            price_distribution = Product.objects.values_list('price', flat=True)
            data = {
                'revenue': revenue,
                'total_sold_products': total_sold_products,
                'highest_sold_product': {
                    'name': highest_sold_product.name,
                    'quantity_sold': highest_sold_product.quantity_sold,
                    'id': str(highest_sold_product.id)
                },
                'average_order_value': average_order_value,
                'price_distribution': price_distribution
            }
            return Response({'data': data}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        