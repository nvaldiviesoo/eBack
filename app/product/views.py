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
from .service_products import authenticate_staff, create_stock_dict, handle_put_request, create_image_dict, create_id_dict, create_stock_dict_by_id, create_image_dict_with_id, create_id_dict_for_color, validate_category, validate_color, validate_size, validate_gender, validate_name, validate_price, validate_quantity

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    """Only admin users actions"""

    @action(methods=['post'], detail=False)
    def add_product(self, request):
        # """Handle creating a new product"""
        
        # Por ahora el auth estará apagado para que sea más  fácil probar
        # user = request.user
        # auth = authenticate_staff(user)
        # if auth:
        #     return Response(auth, status=status.HTTP_403_FORBIDDEN)
        if not validate_name(request.data.get('name')):
            return Response({"error": "Invalid name"}, status=status.HTTP_400_BAD_REQUEST)
        if not validate_price(request.data.get('price')):
            return Response({"error": "Invalid price"}, status=status.HTTP_400_BAD_REQUEST)
        if not validate_quantity(request.data.get('quantity')):
            return Response({"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not validate_category(request.data.get('category')) and request.data.get('category'):
            return Response({"error": "Invalid category"}, status=status.HTTP_400_BAD_REQUEST)
        if not validate_color(request.data.get('color')):
            return Response({"error": "Invalid color"}, status=status.HTTP_400_BAD_REQUEST)
        if not validate_size(request.data.get('size')):
            return Response({"error": "Invalid size"}, status=status.HTTP_400_BAD_REQUEST)
        if not validate_gender(request.data.get('gender')) and request.data.get('gender'):
            return Response({"error": "Invalid gender"}, status=status.HTTP_400_BAD_REQUEST)
        
        
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        serializer = self.serializer_class(data=request.data)
        try:
            if serializer.is_valid():
                
                #comprobar que no existe un prodcto con el mismo nombre y misma talla, color y tamaño (uno de los tres puede ser diferente)
                if not self.queryset.filter(name=serializer.validated_data['name'], size=serializer.validated_data['size'], color=serializer.validated_data['color']).exists():
                    serializer.save(user=user)
                    return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)

                return Response({'data': {"error": "Ya existe este item"}}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False)           
    def add_multiple_products(self, request):
        """Request multiple products """

        user = request.user
        auth = authenticate_staff(user)
        if auth:
            return Response(auth, status=status.HTTP_403_FORBIDDEN)

        return_list = [] # Esta lista va a retornar los errores de cada producto que se crearan
        for product in request.data.get("products"):
            return_dict = {"name": None, "error": None}
            if not validate_name(product.get('name')):
                return_dict["error"] = "Invalid name"
                return_list.append(return_dict)
                continue
            return_dict["name"] = product.get('name')

            if not validate_price(product.get('price')):
                return_dict["error"] = "Invalid price"
                return_list.append(return_dict)
                continue

            if not validate_quantity(product.get('quantity')):
                return_dict["error"] = "Invalid quantity"
                return_list.append(return_dict)
                continue

            if not validate_category(product.get('category')) and product.get('category'):
                return_dict["error"] = "Invalid category"
                return_list.append(return_dict)
                continue

            if not validate_color(product.get('color')):
                return_dict["error"] = "Invalid color"
                return_list.append(return_dict)
                continue

            if not validate_size(product.get('size')):
                return_dict["error"] = "Invalid size"
                return_list.append(return_dict)
                continue
            if not validate_gender(product.get("gender")):
                return_dict["error"] = "Invalid gender" # Dangerous move
                return_list.append(return_dict)
                continue

            serializer = self.serializer_class(data=product)

            try:
                if serializer.is_valid():
                    if not self.queryset.filter(name=serializer.validated_data['name'], size=serializer.validated_data['size'], color=serializer.validated_data['color']).exists():
                        return_dict["error"] = "Producto creado sin errores"
                        serializer.save(user=user)
                    else: 
                        return_dict["error"] = "Ya existe este item"
                else:
                    return_dict["error"] = serializer.errors
            except:
                return_dict["error"] = serializer.errors
            return_list.append(return_dict)

        for product in return_list:
            if product["error"] == "Producto creado sin errores":
                return Response({'data': return_list}, status=status.HTTP_201_CREATED)
            else:
                return Response({'data': return_list}, status=status.HTTP_202_ACCEPTED)
    

    def put(self, request, *args, **kwargs):
        """Handle updating an object"""
        user = request.user
        auth = authenticate_staff(user)
        if auth:
            return Response(auth, status=status.HTTP_403_FORBIDDEN)
        
        product_id = request.data.get('id')
        product = self.queryset.get(id=product_id)
        
        # A continuación, se debe recuperar el tamaño porque django no deja no actualizarlo a pesar de no ser nulo
        request_data = handle_put_request(request, product)

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
    
    @action(methods=['delete'], detail=False)
    def delete_product_by_id(self, request):
        """Handle deleting a product"""
        
        user = request.user
        auth = authenticate_staff(user)
        if auth:
            return Response(auth, status=status.HTTP_403_FORBIDDEN)
        
        product_id = request.query_params.get('id')
        product = self.queryset.filter(id=product_id).first()
        if not product:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        product.delete()
        return Response({'data': 'Product deleted'}, status=status.HTTP_200_OK)

    @action(methods=['patch'], detail=False)
    def edit_product_discount(self, request):
        """Handle editing discount of a product"""
        
        user = request.user
        auth = authenticate_staff(user)
        if auth:
            return Response(auth, status=status.HTTP_403_FORBIDDEN)
        
        try:
            product_id = request.data.get('id')
            product = self.queryset.filter(id=product_id).first()
        except:
            return Response({'error': 'ID must be a valid ID.'}, status=status.HTTP_404_NOT_FOUND)
        if not product:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
        new_discount = request.data.get('discount')
        if new_discount == None:
            return Response({'error': 'Discount is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if int(new_discount) < 0 or int(new_discount) > 100:
                return Response({'error': 'Discount must be between 0 and 100.'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({'error': 'Discount must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)
        
        products = Product.objects.filter(name=product.name, color=product.color).update(discount_percentage=new_discount)
        products = Product.objects.filter(name=product.name, color=product.color) # Actualizamos la lista de productos

        data_serializer = ProductSerializer(products, many=True)

        return Response({'data': data_serializer.data}, status=status.HTTP_200_OK)

    """All users actions"""

    @action(methods=['get'], detail=False)
    def get_products(self, request):
        return Response({'data': self.serializer_class(self.queryset, many=True).data}, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False)
    def get_product_by_id(self, request):
        product_id = request.query_params.get('id')
        try:
            product = Product.objects.get(id=product_id)
            serialized_product = ProductByIdSerializer(product)
            return Response(serialized_product.data, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Product not found"}, status=404)
        

    @action(methods=['get'], detail=False)
    def get_product_by_name(self, request):
        
        product_name = request.query_params.get('name')
        product = Product.objects.filter(name=product_name)
        if not product.exists():
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        stock_dict = create_stock_dict(product)
        image_dict = create_image_dict(product)
        id_dict = create_id_dict(product)
        serialized_product = ProductForShowSerializer(product[0]) # Utilizamos el primer producto, porque deberían ser todos iguales en teoría.

        return Response({"data" : serialized_product.data, "quantity": stock_dict, "ids": id_dict, "color_photo": image_dict}, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=False)
    def get_all_product_by_id(self, request):
        
        try:
            product_id = request.query_params.get('id')
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        
        if product is None:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        products = Product.objects.filter(name=product.name)
        if not products.exists():
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        stock_dict = create_stock_dict(products)
        image_dict = create_image_dict(products)
        id_dict = create_id_dict(products)
        serialized_product = ProductSerializer(product)

        return Response({"data" : serialized_product.data, "quantity": stock_dict, "ids": id_dict, "color_photo": image_dict}, status=status.HTTP_200_OK)
    
        
    @action(methods=['get'], detail=False)
    def filter_products(self, request):
        """Handle filtering products by category"""
            
        category = request.query_params.get('category')
        if not category:
            return Response({'error': 'Category is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        products = Product.objects.filter(category=category)
        if not products.exists():
            return Response({'error': 'Products not found for this category'}, status=status.HTTP_404_NOT_FOUND)
        
        # Solo mandaremos uno de cada color y nombre, independiente de la tallas
        products_dict = {}
        # Podría  ser lento, tal vez sea mejor solo presentar uno por nombre y así es una sola quary
        for product in products:
            products_dict[product.name, product.color] = product
        products = list(products_dict.values())

        serialized_products = ProductForShowSerializer(products, many=True)
        return Response({"data" : serialized_products.data}, status=status.HTTP_200_OK)

      
    @action(methods=['get'], detail=False)
    def get_product_by_id_specific_color(self, request):
        try:
            product_id = request.query_params.get('id')
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        if product is None:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        products = Product.objects.filter(name=product.name, color=product.color)
        if not products.exists():
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
        stock_dict = create_stock_dict_by_id(products, product)
        image_dict = create_image_dict_with_id(products)
        id_dict = create_id_dict_for_color(products, product)
        serialized_product = ProductSerializer(product)

        return Response({"data" : serialized_product.data,
                         "quantity": stock_dict,
                         "color_photo": image_dict,
                         "ids": id_dict}, status=status.HTTP_200_OK)

