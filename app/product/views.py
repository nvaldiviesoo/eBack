"""
Product views
"""

from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser

from core.models import Product, User

from .serializers import ProductSerializer, ProductByIdSerializer, ProductForShowSerializer
from .service_products import authenticate_staff, create_stock_dict, handle_put_request

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    """Only admin users actions"""

    @action(methods=['post'], detail=False)
    def add_product(self, request):
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            
            #comprobar que no existe un prodcto con el mismo nombre y misma talla, color y tamaño (uno de los tres puede ser diferente)
            if not self.queryset.filter(name=serializer.validated_data['name'], size=serializer.validated_data['size'], color=serializer.validated_data['color']).exists():
                serializer.save(user=user)
                return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)

            return Response({'data': {"error": "Ya existe este item"}}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    """All users actions"""

    @action(methods=['get'], detail=False)
    def get_products(self, request):
        return Response({'data': self.serializer_class(self.queryset, many=True).data}, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_product_by_id(self, request):
        product_id = request.query_params.get('id')
        product = Product.objects.get(id=product_id)

        serialized_product = ProductByIdSerializer(product)

        return Response(serialized_product.data, status=status.HTTP_200_OK)
    
        
    def put(self, request, *args, **kwargs):
        """Handle updating an object"""
        
        user = request.user
        auth = authenticate_staff(user)
        if auth:
            return Response(auth, status=status.HTTP_403_FORBIDDEN)
        
        product_id = request.data.get('id')
        product = self.queryset.get(id=product_id)
        # A continuación, se debe recuperar el tamaño porque django no deja no actualizarlo a pesar de no ser nulo
        
        # TODO: Cambiar a una función parte para que no esté en el controlador
        request_data = handle_put_request(request, product)
        
        # Flujo normal
        data_serializer = ProductSerializer(product, data=request_data)
        if data_serializer.is_valid():
            data_serializer.save()
        else:
            return Response(data_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'method': 'PUT', "id": product.id, 'data': data_serializer.data}, status=status.HTTP_200_OK)
    
    @action(methods=['put'], detail=False)
    def stock_update(self, request, *args, **kwargs):
        """Handle updating ONLY stock of a product"""
        
        user = request.user
        auth = authenticate_staff(user)
        if auth:
            return Response(auth, status=status.HTTP_403_FORBIDDEN)
        
        product_id = request.data.get('id')
        product = self.queryset.filter(id=product_id).first()
        if not product:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        new_stock = request.data.get('quantity')
        if new_stock == None:
            # OJO: Estandarizar este error 
            return Response({'error': 'Quantity is required.'}, status=status.HTTP_400_BAD_REQUEST)
        data_serializer = ProductSerializer(product, data={'quantity': new_stock}, partial=True)
        if data_serializer.is_valid():
            data_serializer.save()
        else:
            return Response(data_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'data': data_serializer.data}, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_product_by_name(self, request):
        
        product_name = request.query_params.get('name')
        product = Product.objects.filter(name=product_name)
        if not product.exists():
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        stock_dict = create_stock_dict(product)
        serialized_product = ProductForShowSerializer(product[0]) # Utilizamos el primer producto, porque deberían ser todos iguales en teoría. Excepto por la imágen ahora que lo pienso.

        return Response({"data" : serialized_product.data, "quantity": stock_dict }, status=status.HTTP_200_OK)