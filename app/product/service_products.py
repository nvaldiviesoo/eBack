from core.models import Product

def authenticate_staff(user):
    '''Check if user is authenticated and is an admin.'''
    if not user.is_authenticated:
        return {'error': 'Not authenticated'}
    if not user.is_staff:
        return {'error': 'You are not an admin.'}
    # Retornar falso si no hay errores. Es contraintuitivo con el nombre del método, pero si es TRUE es porque lleva un mensaje de error
    return False


def handle_put_request(request, product):
    ''' Django no deja no actualizar las siguientes variables, así que se necesitan setear a su valor original'''
    
    if "size" not in request.data:
        product_size = product.size
    else:
        product_size = request.data["size"]
    
    if "description" not in request.data:
        product_description = product.description
    else:
        product_description = request.data["description"]
        
    if "name" not in request.data:
        product_name = product.name
    else: 
        product_name = request.data["name"]
    
    request_data = request.data.copy() # request.data es inmutable
    request_data.update({'size': product_size, 'description': product_description, "name": product_name}) # se updatea size con el valor original
    return request_data


def create_stock_dict(products_array):
    '''Crea un diccionario para que el frontend pueda saber el stock de cada color-talla de un producto (recordar que existen multiples instancias)'''
    stock_dict = {}
    for p in products_array:
        stock_dict[p.color] =  {}
    for p in products_array:
        stock_dict[p.color][p.size] = p.quantity
    return stock_dict
def create_image_dict(products_array):
    '''Crea un diccionario para que el frontend pueda saber la imagen de cada color-talla de un producto (recordar que existen multiples instancias)'''
    image_dict = {}
    for p in products_array:
        image_dict[p.color] =  {}
    return image_dict

def create_stock_dict_by_id(products_array, product_initial):
    '''Crea un diccionario para que el frontend pueda saber el stock de cada talla de un producto-color (recordar que existen multiples instancias)'''
    stock_dict = {}
    for p in Product.SIZE_OPTIONS:
        stock_dict[p[0]] = 0
        
    for p in products_array:
        if p.color == product_initial.color:
            stock_dict[p.size] = p.quantity
    return stock_dict

def create_image_dict_with_id(products_array):
    '''Crea un diccionario para que el frontend pueda saber la imagen e id de cada color de un producto )'''
    image_dict = {}
    for p in products_array:
        if p.image:
            image_dict[p.color] =  {"id": p.id, "image": p.image.url}
        else:
            image_dict[p.color] =  {"id": p.id, "image": "Null"}
    return image_dict


def create_id_dict(products_array):
    '''Crea un diccionario para que el frontend pueda saber la id de cada color-talla de un producto (recordar que existen multiples instancias)'''
    id_dict = {}
    for p in products_array:
        id_dict[p.color] =  {}
    for p in products_array:
        id_dict[p.color][p.size] = p.id
    return id_dict