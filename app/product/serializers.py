
from rest_framework import serializers
from core.models import Product

class ProductSerializer(serializers.ModelSerializer):

    user_name = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.name

    class Meta:
        model = Product
        fields = '__all__'