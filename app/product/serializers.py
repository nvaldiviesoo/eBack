
from rest_framework import serializers
from core.models import Product

class ProductSerializer(serializers.ModelSerializer):

    user_name = serializers.SerializerMethodField()

    def get_user_name(self, obj):
        return obj.user.name

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'user_name',
                  "discount_percentage" , 'user', 'created_at', 'updated_at',
                  'image', 'category', "gender", "size", "color", "quantity"]
        readl_only_fields = ['user_name', 'user', 'created_at', 'updated_at']


class ProductByIdSerializer(serializers.ModelSerializer):

    user_name = serializers.SerializerMethodField()

    def get_user_name(self, obj):
        return obj.user.name

    class Meta:
        model = Product
        fields = "__all__"# Podría ser necesario agregar el resto, o poner "__all__" para mostrar todos los campos
        read_only_fields = ['user_name', 'user', 'created_at', 'updated_at']
        
        
class ProductForShowSerializer(serializers.ModelSerializer):

    user_name = serializers.SerializerMethodField()

    def get_user_name(self, obj):
        return obj.user.name

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'user_name',
                  "discount_percentage" , 'user', 'created_at', 'updated_at',
                  'image', 'category', "gender"]
        read_only_fields = ['user_name', 'user', 'created_at', 'updated_at']