from rest_framework import serializers

from core.models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items"""
    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders"""
    order_items = serializers.SerializerMethodField(method_name='get_order_items')

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'total_amount')

    def get_order_items(self, obj):
        """Retrieve order items"""
        order_items = obj.order_items.all()
        return OrderItemSerializer(order_items, many=True).data
