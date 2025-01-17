"""
Views for the user API. Here we are going to define sign up, login, reset password, etc.
"""

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from datetime import datetime

from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from core.models import User
from core.utils.send_email import send_forgot_password_email

from .serializers import UserSerializer, UserAdminViewSerializer


class UserModelViewSet(ModelViewSet):
  """User viewset."""

  queryset = User.objects.all()
  serializer_class = UserSerializer
  
  @action(methods=['delete'], detail=False)
  def delete(self, request, *args, **kwargs):

    active_user = request.user
    if not active_user.is_authenticated:
        return Response({'error': 'Not authenticated'}, status=status.HTTP_403_FORBIDDEN)
    if not active_user.is_staff:
        return Response({'error': 'You are not an admin.'}, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('id')
    user = User.objects.get(id=user_id)
    user.delete()
    

    return Response({'message': 'User deleted successfully', 'status': status.HTTP_204_NO_CONTENT})

  @action(methods=['post'], detail=False)
  def sign_up(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    if serializer.is_valid():
      user = serializer.save()

      refresh = RefreshToken.for_user(user)
      token = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
      }
      return Response({'data': serializer.data, 'token': token, 'status':status.HTTP_201_CREATED   })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  @action(methods=['post'], detail=False)
  def forgot_password(self, request, *args, **kwargs):
    data = request.data

    user = get_object_or_404(User, email=data['email'])

    token = RefreshToken.for_user(user)

    send_forgot_password_email(user.email, token)

    return Response({'message': f'Password reset email sent to {user.email}', 'status': status.HTTP_200_OK})
  
  @action(methods=['get'], detail=False)
  def me(self, request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
      serializer = UserSerializer(user)
      return Response({'data': serializer.data}, status=status.HTTP_200_OK)
    else:
      return Response({'error': 'Not authenticated'}, status=status.HTTP_403_FORBIDDEN)
  
  @action(methods=['PUT'], detail=False)
  def edit_profile(self, request, *args, **kwargs):
    user = request.user
    if not user.is_authenticated:
      return Response({'error': 'Not authenticated'}, status=status.HTTP_403_FORBIDDEN)
    data = request.data
    if 'name' not in data:
      return Response({'error': 'Name field is required'}, status=status.HTTP_400_BAD_REQUEST)
    if 'email' in data:
      return Response({'error': 'Email field should not be included'}, status=status.HTTP_400_BAD_REQUEST)
    if 'password' in data:
      return Response({'error': 'Password field should not be included'}, status=status.HTTP_400_BAD_REQUEST)
    if 'is_superuser' in data or 'balance' in data or 'is_staff' in data:
      return Response({'error': 'You are not authorized to edit this field'}, status=status.HTTP_403_FORBIDDEN)
    if len(data['name']) <= 5: 
      return Response({'error': 'Name field should not be less than 5 characters'}, status=status.HTTP_400_BAD_REQUEST)
    if len(data['name']) > 50:
      return Response({'error': 'Name field should not exceed 50 characters'}, status=status.HTTP_400_BAD_REQUEST)
    if 'birth_date' in data:
      if data['birth_date'] == '':
        return Response({'error': 'Birth date should not be empty'}, status=status.HTTP_400_BAD_REQUEST)
      elif type(data['birth_date']) != str:
        return Response({'error': 'Invalid birth_date format, should be YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
      else:
        try:
          parsed_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
          user.birth_date = parsed_date
        except ValueError:
          return Response({'error': 'Invalid birth_date format, should be YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
    user.name = data['name']
    user.save()

    serializer = UserSerializer(user)
    return Response({'data': serializer.data}, status=status.HTTP_200_OK)

  @action(methods=['GET'], detail=False)
  def all(self, request, *args, **kwargs):
    active_user = request.user
    if not active_user.is_authenticated:
      return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    if not active_user.is_staff:
      return Response({'error': 'You are not an admin.'}, status=status.HTTP_403_FORBIDDEN)
    
    users = User.objects.all()
    serializer = UserAdminViewSerializer(users, many=True)
    return Response({'data': serializer.data, 'status': status.HTTP_200_OK})

  
  @action(methods=['PUT'], detail=False)
  def staff(self, request, *args, **kwargs):
    user = request.user
    if not user.is_authenticated:
      return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    # TODO: Que sea superuser en lugar de staff
    if not user.is_staff:
      return Response({'error': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
    if not 'id' in request.query_params:
      return Response({'error': 'User id is required'}, status=status.HTTP_400_BAD_REQUEST)
    if not 'is_staff' in request.data:
      return Response({'error': 'is_staff field is required'}, status=status.HTTP_400_BAD_REQUEST)
    user_id = request.query_params.get('id')
    if str(user.id) == user_id:
      return Response({'error': 'You cannot change your own staff status'}, status=status.HTTP_403_FORBIDDEN)
    try:
      user = User.objects.get(id=user_id)
      new_staff = request.data.get('is_staff') 
      user.is_staff = new_staff
      user.save()

      serializer = UserSerializer(user)
      return Response({'data': serializer.data})
    except User.DoesNotExist:
      return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
  
  @action(methods=['patch'], detail=False) 
  def edit_balance(self, request, *args, **kwargs):
    user = request.user
    if not user.is_authenticated:
      return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    if not user.is_staff:
      return Response({'error': 'You are not authorized to perform this action'}, status=status.HTTP_403_FORBIDDEN)
    
    if not 'id' in request.data.keys():
      return Response({'error': 'User id is required'}, status=status.HTTP_400_BAD_REQUEST)
    if not 'balance' in request.data.keys():
      return Response({'error': 'Balance field is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    user_id = request.data.get('id')
    try:
      user = User.objects.get(id=user_id)
      add_balance = request.data.get('balance')
      try:
        add_balance = float(add_balance)
      except ValueError:
        return Response({'error': 'Balance should be a number'}, status=status.HTTP_400_BAD_REQUEST)
      if add_balance < 0:
        return Response({'error': 'Balance should not be negative'}, status=status.HTTP_400_BAD_REQUEST)
      
      user.balance += add_balance
      user.save()

      serializer = UserSerializer(user)
      return Response({'data': serializer.data})
    except User.DoesNotExist:
      return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
      
    

class CustomLoginView(TokenObtainPairView):

  def post(self, request, *args, **kwargs):
    username = request.data.get('email', None)
    password = request.data.get('password', None)

    user = authenticate(request, username=username, password=password)
    if user is not None:
      user_data = {
        'username': user.name,
        'email': user.email,
        'is_superuser': user.is_superuser,
      }
      response = super().post(request, *args, **kwargs)
      response.data['user'] = user_data
      return Response({'data': response.data, 'status': status.HTTP_200_OK})
    else:
      return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)