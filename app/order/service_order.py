def authenticate_staff(user):
    '''Check if user is authenticated and is an admin.'''
    #! OJO, esta función se reptite en products. tal vez se pueda mover a otro lado.
    #Todo: Mover a un archivo de utilidades
    if not user.is_authenticated:
        return {'error': 'Not authenticated'}
    if not user.is_staff:
        return {'error': 'You are not an admin.'}
    # Retornar falso si no hay errores. Es contraintuitivo con el nombre del método, pero si es TRUE es porque lleva un mensaje de error
    return False