"""
Views for the user API. Here we are going to define sign up, login, reset password, etc.
"""

from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from core.models import User
from core.utils.send_email import send_forgot_password_email

from .serializers import UserSerializer


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
    
    user.name = data['name']
    user.save()

    serializer = UserSerializer(user)
    return Response({'data': serializer.data})

  @action(methods=['GET'], detail=False)
  def all(self, request, *args, **kwargs):
    active_user = request.user
    if not active_user.is_authenticated:
      return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
    if not active_user.is_staff:
      return Response({'error': 'You are not an admin.'}, status=status.HTTP_403_FORBIDDEN)
    
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response({'data': serializer.data, 'status': status.HTTP_200_OK})
      
    

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